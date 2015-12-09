from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.models import LightDevice, new_event, FlowerData, WaterDevice, GrowSession
from app import appbuilder, db, app, hub
from flask import current_app
import logging

scheduler = None


def meassure():
    """ Measures the FlowerDevices of all active GrowSessions. Waters if their
    water is under the WaterDevice threshhol.
    Returns:

    """
    if app.config['HARDWARE']:
        from app.hardware import flower_power
    result = []
    for grow_session in GrowSession.get_active():
        result += grow_session.flower_devices
    if len(result) == 0:
        print("Nothing to meassure")
        return
    for flower_device in result:
        if app.config['HARDWARE']:
            data = flower_power.get_flower_data(flower_device.mac)
        else:
            data = dict(Temperature=10.23, Light=100, Water=50.0, Battery=90, Ecb=0.5,
                        EcPorus=0.6, DLI=0.7, Ea=0.8, )
        flower_data = FlowerData.new_flower_data(data, flower_device.id, flower_device.grow_session.id)
        db.session.add(flower_data)
        db.session.commit()
        hub.new_data_point(flower_data)
        new_event("Meassure Flower_device " + flower_device.mac)
        # Check if we have to water.
        for water_device in flower_device.grow_session.water_devices:
            if data['Water'] < water_device.water_threshhold:  # Have to water.
                start_water(water_device.id)
    logging.getLogger().warning("Meassure completed")


def switch_light(light_id, on):
    """ Switches light to state of the variable on.
    Args:
        light_id (str): The database id from the Light.
        on (bool): True if the light should be turned on, False if off.

    Returns:

    """
    light_device = appbuilder.session.query(LightDevice).filter(LightDevice.id == light_id).first()
    if current_app.config['HARDWARE']:
        from app.hardware import remote_socket

        remote_socket.switch(map(int, light_device.key), light_device.device, on)
    light_device.state = on
    db.session.commit()
    new_event("Switch Light " + light_device.name + " to " + str(light_device.state))


def switch_light_on(light_id):
    """ Switches the light light_id to on.
    Args:
        light_id (str): The id of the LightDevice.

    Returns:

    """
    switch_light(light_id, True)


def switch_light_off(light_id):
    """ Switches the light light_id to off.
    Args:
        light_id (str): The id of the LightDevice.

    Returns:

    """
    switch_light(light_id, False)


def switch_water_to(water_device, on):
    """ Switches the water_device to state on
    Args:
        water_device: The id of the WaterDevice
        on (bool): On / Off

    Returns:

    """
    if water_device.state() == on:  # Already right state.
        return
    if current_app.config['HARDWARE']:
        from app.hardware import remote_socket
        remote_socket.switch(map(int, water_device.key), water_device.device, on)


def start_water(water_id):
    """ Starts the WaterDevice with water_id and starts the task to turn
    it off.
    Args:
        water_id (str): The id of the WaterDevice.
    Returns:

    """
    water_device = appbuilder.session.query(WaterDevice).filter(WaterDevice.id == water_id).first()
    switch_water_to(water_device, True)
    water_device.switch_off_time = datetime.now() + timedelta(minutes=water_device.watering_duration_minutes)
    db.session.commit()
    scheduler.add_job(stop_water, 'date', run_date=water_device.switch_off_time, args=[water_device.id],
                      misfire_grace_time=10000000, id='water_off_' + water_device.name)
    new_event("Switch Water " + water_device.name + " to True")


def stop_water(water_id):
    """ Stops the WaterDevice.
    Args:
        water_id (str): The id of the WaterDevice.

    Returns:

    """
    water_device = appbuilder.session.query(WaterDevice).filter(WaterDevice.id == water_id).first()
    switch_water_to(water_device, False)
    water_device.switch_off_time = None
    db.session.commit()
    new_event("Switch Water " + water_device.name + " to False")


def switch_water(water_id):
    """ Switches the WaterDevice -> When it's on turn it off and when it's off on
    Args:
        water_id (str): The id of the WaterDevice

    Returns:

    """
    water_device = appbuilder.session.query(WaterDevice).filter(WaterDevice.id == water_id).first()
    if water_device.state():
        stop_water(water_id)
        return
    else:
        start_water(water_id)
        return


def update_subscribers():
    """ Updates all Subscribers of active GrowSessions
    Returns:

    """
    for active_grow_session in GrowSession.get_active():
        subscribers = active_grow_session.subscribers
        if len(subscribers) == 0:
            continue
        newest_data_point = appbuilder.session.query(FlowerData) \
            .filter(FlowerData.grow_session_id == active_grow_session.id) \
            .order_by(FlowerData.timestamp.desc()).first()
        if newest_data_point is None:  # If no data in GrowSession just skip.
            continue
        data = newest_data_point.get_data_dict()
        for subscriber in subscribers:
            receiver = subscriber.receiver_email
            subject = "Flower Data " \
                      + newest_data_point.grow_session.name \
                      + " " + data['TimeStamp'] + " Water: " \
                      + data['Water']
            body = ""
            for attribute in data:
                body += attribute + " " + data[attribute] + "\n"
            hub.send_email(receiver, subject, body)
            new_event("Send email to " + subscriber.name)


def webcam():
    if app.config["WEBCAM"]:
        from app.hardware import webcam
        filename = webcam.webcam_make_screenshot()
        hub.new_webcam_screenshot(filename)
        new_event("Made screenshot")


def start_light_task(light_device):
    scheduler.add_job(switch_light_on, 'cron',
                      hours=light_device.day_start_hour,
                      misfire_grace_time=10000000,
                      args=[light_device.id],
                      id='light_on_' + light_device.name)
    scheduler.add_job(switch_light_off, 'cron',
                      hours=light_device.night_start_hour,
                      misfire_grace_time=10000000,
                      args=[light_device.id],
                      id='light_off_' + light_device.name)
    if (light_device.night_start_hour > datetime.now().hour
            > light_device.day_start_hour):  # Day = light on.
        switch_light_on(light_device.id)
    else:
        switch_light_off(light_device.id)


def start_scheduler():
    """ Creates the scheduler and adds all basic tasks.
    Returns:

    """
    global scheduler
    scheduler = BackgroundScheduler(executors=current_app.config['SCHEDULER_EXECUTORS'],
                                    job_defaults=current_app.config['SCHEDULER_DEFAULTS'])
    scheduler.remove_all_jobs()
    scheduler.add_job(meassure, 'cron', minute='0,15,30,45', id='meassure')
    # Light devices.
    for light_device in LightDevice.get_active():
        start_light_task(light_device)
    # Water devices.
    for active_water_device in WaterDevice.get_turned_on():
        if active_water_device.switch_off_time <= datetime.now():  # switch now if event in past
            stop_water(active_water_device.id)
        else:
            scheduler.add_job(stop_water, 'date', run_date=active_water_device.switch_off_time,
                              args=[active_water_device.id],
                              misfire_grace_time=10000000,
                              id='water_on_' + active_water_device.name)
    # Subscribers.
    scheduler.add_job(update_subscribers, 'cron',
                      hour='15', id='update_subscribers')
    # Webcam
    scheduler.add_job(webcam, 'cron',
                      minute='1,31', id='webcam')
    webcam()
    print("Scheduler started")
    scheduler.start()
