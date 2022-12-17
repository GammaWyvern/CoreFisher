import dxcam;
import cv2;
import os.path;
from pymouse import PyMouse;

# Setup images resource path
res = os.path.join(os.path.dirname(__file__), "res\\");
if (not os.path.exists(res)):
    raise Exception("Image resource folder unreadable")

# Create file paths for fishing images
imgCatch = os.path.join(res, "fishFound.png");
imgPull = os.path.join(res, "fishPull.png");
imgStopPull = os.path.join(res, "fishNoPull.png");

# Ensure all neccesary images can be loaded
if (not os.path.exists(imgCatch)):
    raise Exception("Image file(s) not found");
if (not os.path.exists(imgPull)):
    raise Exception("Image file(s) not found");
if (not os.path.exists(imgStopPull)):
    raise Exception("Image file(s) not found");

# Load actual images
imgCatch = cv2.imread(imgCatch, cv2.IMREAD_GRAYSCALE);
imgPull = cv2.imread(imgPull, cv2.IMREAD_GRAYSCALE);
imgStopPull = cv2.imread(imgStopPull, cv2.IMREAD_GRAYSCALE);

# Vars for mouse input
mouse = PyMouse();
screenWidth, screenHeight = mouse.screen_size();
catching = False;
reelingIn = False;

# Start screen recording
screenCam = dxcam.create();
screenCam.start(target_fps=20);

while (True):
    screen = cv2.cvtColor(screenCam.get_latest_frame(), cv2.COLOR_RGB2GRAY);

    catchResults = cv2.matchTemplate(screen, imgCatch, cv2.TM_SQDIFF_NORMED);
    catchResult = cv2.minMaxLoc(catchResults)[0] < 0.2;

    pullResults = cv2.matchTemplate(screen, imgPull, cv2.TM_SQDIFF_NORMED);
    pullResult = cv2.minMaxLoc(pullResults)[0] < 0.35;

    stopPullResults = cv2.matchTemplate(screen, imgStopPull, cv2.TM_SQDIFF_NORMED);
    stopPullResult = cv2.minMaxLoc(stopPullResults)[0] < 0.35;

    # Logic

    # Click to pull in fish and latch pullingThing
    if (catchResult and not catching):
        mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
        catching = True;
    
    # Unlatch pullingThing when catch picture is gone
    if (not catchResult and catching):
        catching = False;

    # Update mouse press for pulling in fish
    if (pullResult and not reelingIn):
        mouse.press(int(screenWidth/2), int(screenHeight/2), button=2);
        reelingIn = True;
    elif (stopPullResult and reelingIn):
        mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
        reelingIn = False;
    # After fish is caught release mouse
    elif (reelingIn and not pullResult and not stopPullResult):
        mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
        pullResult = False;