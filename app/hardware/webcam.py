import subprocess


def webcam_make_screenshot():
    """
    Returns: The screenshot filename
    """

    subprocess.call("fswebcam -d /dev/video0  -S 2 -s brightness=60% " +
                    "-s Contrast=15%  -s Gamma=50%  -p YUYV -r 1280x720 " +
                    "webcam.jpg --jpeg 80 -s Sharpness=40% -s Saturation=15%",
                    shell=True)
    return "webcam.jpg"
