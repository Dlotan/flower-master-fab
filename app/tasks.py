from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.models import LightDevice, new_event, FlowerData, WaterDevice, GrowSession

scheduler = None


def meassure():
    from app.hardware import flower_power
    from app import db

    result = []
    for grow_session in GrowSession.get_active():
        result += grow_session.flower_devices
    for flower_device in result:
        data = flower_power.get_flower_data(flower_device.mac)
        db.session.add(FlowerData.new_flower_data(data, flower_device.id, flower_device.grow_session.id))
        db.session.commit()
        new_event("Meassure Flower_device " + flower_device.mac)
        # check if we have to water
        for water_device in flower_device.grow_session.water_devices:
            if data['water'] < water_device.water_threshhold:  # have to water
                start_water(water_device.id)
    print("Meassure completed")


def switch_light(light_id):
    from app import appbuilder, db, app

    light_device = appbuilder.session.query(LightDevice).filter(LightDevice.id == light_id).first()
    if app.config['PI']:
        from app.hardware import remote_socket
        remote_socket.switch(map(int, light_device.key), light_device.device, not light_device.state)
    if light_device.state:  # turn off
        time = light_device.grow_session.night_hours
    else:
        time = light_device.grow_session.day_hours
    light_device.next_switch = datetime.now() + timedelta(hours=time)
    light_device.state = not light_device.state
    db.session.commit()
    if light_device.grow_session.is_active():
        scheduler.add_job(switch_light, 'date', run_date=light_device.next_switch, args=[light_device.id],
                          misfire_grace_time=10000000, id='water' + light_device.name)
    new_event("Switch Light " + light_device.name + " to " + str(light_device.state))


def start_water(water_id):
    from app import appbuilder, db

    water_device = appbuilder.session.query(WaterDevice).filter(WaterDevice.id == water_id).first()
    if water_device.state():  # already turned on
        return
    from app.hardware import remote_socket

    remote_socket.switch(map(int, water_device.key), water_device.device, True)
    water_device.switch_off_time = datetime.now() + timedelta(minutes=water_device.watering_duration_minutes)
    db.session.commit()
    scheduler.add_job(stop_water, 'date', run_date=water_device.switch_off, args=[water_device.id],
                      misfire_grace_time=10000000, id='water' + water_device.name)
    new_event("Switch Water " + water_device.name + " to True")


def stop_water(water_id):
    from app import appbuilder, db

    water_device = appbuilder.session.query(WaterDevice).filter(WaterDevice.id == water_id).first()
    from app.hardware import remote_socket

    remote_socket.switch(water_device.key, water_device.device, False)
    water_device.switch_off_time = None
    db.session.commit()
    new_event("Switch Water " + water_device.name + " to False")


def start_scheduler():
    global scheduler
    scheduler = BackgroundScheduler()
    scheduler.remove_all_jobs()
    scheduler.add_job(meassure, 'cron', minute="0,15,30,45", id="meassure")
    for active_light_device in LightDevice.get_active():
        if active_light_device.next_switch <= datetime.now():  # switch now if event in past
            switch_light(active_light_device.id)
        else:
            scheduler.add_job(switch_light, 'date', run_date=active_light_device.next_switch,
                              args=[active_light_device.id],
                              misfire_grace_time=10000000,
                              id='light' + active_light_device.name)

    for active_water_device in WaterDevice.get_turned_on():
        if active_water_device.switch_off_time <= datetime.now():  # switch now if event in past
            stop_water(active_water_device.id)
        else:
            scheduler.add_job(stop_water, 'date', run_date=active_water_device.switch_off_time,
                              args=[active_water_device.id],
                              misfire_grace_time=10000000,
                              id='water' + active_water_device.name)
    scheduler.start()
