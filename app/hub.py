from app import app
import json
import requests


def send_email(receiver, subject, body):
    """ Send email by using the hub.
    Args:
        receiver (str): The email address of the person the email should be send to.
        subject (str): The subject of the email.
        body (str): The body of the email.

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
    """ Uploads the screenshot filename to the hub.
    Args:
        filename: The filename of the file which should be pushed to the hub.

    Returns:

    """
    r = requests.post(app.config["HUB_URL"] + "/flower/new_picture",
                      files={filename: open(filename, 'rb')})
    return r.status_code == 200


def new_webcam_gif(filename):
    """ Uploads the screenshot filename to the hub.
    Args:
        filename: The filename of the file which should be pushed to the hub.

    Returns:

    """
    r = requests.get(app.config["HUB_URL"] + "/flower/new_gif")
    blob_url = r.text
    r = requests.post(blob_url,
                      files={"file": open(filename, 'rb')})
    return r.status_code == 200