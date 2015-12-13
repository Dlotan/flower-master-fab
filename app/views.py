from flask.ext.appbuilder.actions import action
from flask.ext.appbuilder.charts.views import DirectByChartView
from flask import render_template, redirect
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
# from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from flask.ext.appbuilder import ModelView, BaseView, expose
from datetime import datetime
from app import appbuilder, db
from flask import current_app

from app.models import LightDevice, GrowSession, EventLog, FlowerDevice, FlowerData, Subscriber, new_event, WaterDevice
from app.model_events import on_grow_session_start_hour_changed

class JobsView(BaseView):
    route_base = '/jobs'
    default_view = 'view'

    @expose('/')
    def view(self):
        from app.tasks import scheduler

        jobs = scheduler.get_jobs()
        return render_template('view_jobs.html', base_template=appbuilder.base_template,
                               appbuilder=appbuilder, jobs=jobs)


class SocketManualView(BaseView):
    route_base = '/hardware/socket'
    default_view = 'view'

    @expose('/')
    def view(self):
        if current_app.config['HARDWARE']:
            from app.hardware import remote_socket

            remote_socket.switch([1, 0, 0, 1, 1], 1, False)
        return "bla"


class EventLogModelView(ModelView):
    datamodel = SQLAInterface(EventLog)

    list_columns = ['timestamp', 'text']
    base_order = ('timestamp', 'desc')


class GrowSessionModelView(ModelView):
    datamodel = SQLAInterface(GrowSession)
    related_views = [LightDevice, FlowerDevice, FlowerData]

    list_columns = ['name']

    @action("Start", "Start this session", "Do you really want to?", "fa-rocket")
    def start(self, grow_sessions):

        if isinstance(grow_sessions, list):
            grow_session = grow_sessions[0]
        else:
            grow_session = grow_sessions

        grow_session.start_date = datetime.now()
        new_event("GrowSession started " + grow_session.name)

        self.update_redirect()
        from tasks import start_light_tasks

        for light_device in grow_session.light_devices:
            start_light_tasks(light_device)
        return redirect(self.get_redirect())


class LightDeviceModelView(ModelView):
    datamodel = SQLAInterface(LightDevice)
    related_views = [GrowSession]

    list_columns = ['name']

    @action("Switch On", "Switch Light Device On", "Do you really want to?", "fa-rocket")
    def switch_on(self, light_devices):
        from app.tasks import switch_light_on

        if isinstance(light_devices, list):
            light_devices = light_devices
        else:
            light_devices = [light_devices]
        self.update_redirect()
        for light_device in light_devices:
            new_event("Switch Light Action " + light_device.name + " on")
            switch_light_on(light_device.id)
        return redirect(self.get_redirect())

    @action("Switch Off", "Switch Light Device Off", "Do you really want to?", "fa-rocket")
    def switch_off(self, light_devices):
        from app.tasks import switch_light_off

        if isinstance(light_devices, list):
            light_devices = light_devices
        else:
            light_devices = [light_devices]
        self.update_redirect()
        for light_device in light_devices:
            new_event("Switch Light Action " + light_device.name + " off")
            switch_light_off(light_device.id)
        return redirect(self.get_redirect())


class WaterDeviceModelView(ModelView):
    datamodel = SQLAInterface(WaterDevice)
    related_views = [GrowSession]

    list_columns = ['name']

    @action("Switch", "Switch Water Device", "Do you really want to?", "fa-rocket")
    def switch(self, water_devices):
        from app.tasks import scheduler, switch_water

        if isinstance(water_devices, list):
            water_devices = water_devices
        else:
            water_devices = [water_devices]
        self.update_redirect()
        for water_device in water_devices:
            job = scheduler.get_job('water_off_' + water_device.name)
            if job:
                job.remove()
            new_event("Switch Water Action " + water_device.name)
            switch_water(water_device.id)
        return redirect(self.get_redirect())


class FlowerDeviceModelView(ModelView):
    datamodel = SQLAInterface(FlowerDevice)
    related_views = [GrowSession]

    list_columns = ['name']


class FlowerDataModelView(ModelView):
    datamodel = SQLAInterface(FlowerData)
    related_views = [GrowSession]


class SubscriberModelView(ModelView):
    datamodel = SQLAInterface(Subscriber)
    related_views = [GrowSession]

    list_columns = ['name']


class FlowerDataChartView(DirectByChartView):
    datamodel = SQLAInterface(FlowerData)
    chart_title = 'Flower Data'
    chart_type = 'LineChart'

    definitions = [
        {
            'label': 'Water',
            'group': 'timestamp',
            'series': ['water']
        },
        {
            'label': 'Light',
            'group': 'timestamp',
            'series': ['light']
        },
        {
            'label': 'Temperature',
            'group': 'timestamp',
            'series': ['temperature']
        },
        {
            'label': 'Battery',
            'group': 'timestamp',
            'series': ['battery']
        },
        {
            'label': 'Ecb',
            'group': 'timestamp',
            'series': ['ecb']
        },
        {
            'label': 'Ec_Porus',
            'group': 'timestamp',
            'series': ['ec_porus']
        },
        {
            'label': 'Dli',
            'group': 'timestamp',
            'series': ['dli']
        },
        {
            'label': 'Ea',
            'group': 'timestamp',
            'series': ['ea']
        },
    ]

db.create_all()
db.event.listen(GrowSession.day_start_hour, 'set', on_grow_session_start_hour_changed)
db.event.listen(GrowSession.night_start_hour, 'set', on_grow_session_start_hour_changed)

appbuilder.add_view(EventLogModelView, "EventLog", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(GrowSessionModelView, "GrowSessions", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(LightDeviceModelView, "LightDevices", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(WaterDeviceModelView, "WaterDevices", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(FlowerDeviceModelView, "FlowerDevices", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(FlowerDataModelView, "FlowerData", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(SubscriberModelView, "Subscriber", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")

appbuilder.add_view(FlowerDataChartView, "FlowerData", icon="fa-folder-open-o", category="View",
                    category_icon="fa-envelope")
appbuilder.add_view(JobsView, "Jobs", category="View")
appbuilder.add_view(SocketManualView, "SocketManual", category="View")
