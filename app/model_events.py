from app import app, tasks
from flask import flash


def on_grow_session_hour_changed(grow_session, value, oldvalue, initiator):
    """

    Args:
        grow_session (app.models.GrowSession):
        value (int):
        oldvalue (int):
        initiator:

    Returns:

    """
    if value not in range(0, 24):  # Only hour 0-23 allowed.
        flash("Can only set night and day start hour from 0-23", "danger")
        return value % 24
    return value


def after_grow_session_update(mapper, connection, grow_session):
    if not app.config['TESTING']:
        if grow_session.is_active():
            for light_device in grow_session.light_devices:
                tasks.stop_light_tasks(light_device)
                tasks.start_light_tasks(light_device)
