from app import app, tasks


def on_grow_session_start_hour_changed(grow_session, value, oldvalue, initiator):
    """

    Args:
        grow_session (app.models.GrowSession):
        value (int):
        oldvalue (int):
        initiator:

    Returns:

    """
    if not app.config['TESTING']:
        if grow_session.is_active():
            for light_device in grow_session.light_devices:
                tasks.stop_light_tasks(light_device)
                tasks.start_light_tasks(light_device)
                tasks.new_event("Set new tasks for " + light_device.name)
