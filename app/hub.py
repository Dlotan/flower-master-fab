from app import app
import json
import requests


def send_email(receiver, subject, body):
    """ Send email by using the
    Args:
        receiver (str):
        subject (str):
        body (str):

    Returns:
        bool: True if successful
    """
    headers = {'content-type': 'application/json'}
    data = dict(
        receiver=receiver,
        subject=subject,
        body=body,
    )
    if app.config['TESTING']:
        return True
    r = requests.post(app.config["HUB_URL"] + "/email/new",
                      headers=headers, data=json.dumps(data))
    return r.status_code == 200


def new_data_point(flower_data):
    """ Post new data to the hub
    Args:
        flower_data (app.models.FlowerData): The flower data

    Returns:
        bool: True if successful
    """
    headers = {'content-type': 'application/json'}
    params = flower_data.get_data_dict()
    params["FlowerName"] = flower_data.flower_device.name
    params["GrowSession"] = flower_data.grow_session.name
    if app.config['TESTING']:
        return True
    r = requests.post(app.config["HUB_URL"] + "/flower/new_data",
                      headers=headers, data=json.dumps(params))
    return r.status_code == 200


def new_webcam_screenshot(filename):
    r = requests.post(app.config["HUB_URL"] + "/flower/new_picture",
                      files={filename: open(filename, 'rb')})
    return r.status_code == 200