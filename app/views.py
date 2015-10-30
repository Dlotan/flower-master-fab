from flask.ext.appbuilder.actions import action
from flask.ext.appbuilder.charts.views import DirectByChartView
from flask import render_template, redirect
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterEqualFunction
from flask.ext.appbuilder import ModelView
from datetime import datetime
from app import appbuilder, db

from app.models import LightDevice, GrowSession, EventLog, FlowerDevice, FlowerData, new_event, WaterDevice

"""
    Application wide 404 error handler
"""


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404


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
        for light_device in grow_session.light_devices:
            light_device.next_switch = datetime.now()
            db.session.commit()
            from app.tasks import switch_light

            switch_light(light_device.id)
        return redirect(self.get_redirect())


class LightDeviceModelView(ModelView):
    datamodel = SQLAInterface(LightDevice)
    related_views = [GrowSession]

    list_columns = ['name']

    @action("Switch", "Switch Light Device", "Do you really want to?", "fa-rocket")
    def switch(self, light_devices):

        if isinstance(light_devices, list):
            light_devices = light_devices
        else:
            light_devices = [light_devices]
        self.update_redirect()
        from app.tasks import scheduler, switch_light
        for light_device in light_devices:
            job = scheduler.get_job('light' + light_device.name)
            if job:
                job.remove()
            new_event("Switch Light Action " + light_device.name)
            switch_light(light_device.id)
        return redirect(self.get_redirect())


class WaterDeviceModelView(ModelView):
    datamodel = SQLAInterface(WaterDevice)
    related_views = [GrowSession]

    list_columns = ['name']


class FlowerDeviceModelView(ModelView):
    datamodel = SQLAInterface(FlowerDevice)
    related_views = [GrowSession]

    list_columns = ['name']


class FlowerDataModelView(ModelView):
    datamodel = SQLAInterface(FlowerData)
    related_views = [GrowSession, FlowerDevice]


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
        }
    ]


db.create_all()
appbuilder.add_view(EventLogModelView, "EventLog", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(GrowSessionModelView, "GrowSessions", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(LightDeviceModelView, "LightDevices", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(FlowerDeviceModelView, "FlowerDevices", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")
appbuilder.add_view(FlowerDataModelView, "FlowerData", icon="fa-folder-open-o", category="Manage",
                    category_icon="fa-envelope")

appbuilder.add_view(FlowerDataChartView, "FlowerData", icon="fa-folder-open-o", category="View",
                    category_icon="fa-envelope")
