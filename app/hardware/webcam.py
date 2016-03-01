import subprocess


def webcam_make_screenshot():
    """
    Returns: The screenshot filename
    """

    subprocess.call("fswebcam -r 320x240 --jpeg 85 -D 1 -S 2 webcam.jpg", shell=True)
    return "webcam.jpg"
