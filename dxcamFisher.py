import dxcam;
import cv2;
import os.path;
from pymouse import PyMouse;
import keyboard;
import time;

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

# Start screen recording
screenCam = dxcam.create();
screenCam.start(target_fps=60);

# Var for actually running thing
runningAutoFish = False;
togglePressed = False;

#Variables for auto fishing
catching = False;
reelingIn = False;
casted = False;
inputTime = time.time(); # Used to recast after fish is caught (or failed)

while (True):
    # Enable/Disable when g is pressed
    if (keyboard.is_pressed("g") and not togglePressed):
        togglePressed = True;

        if (not runningAutoFish):
            catching = False;
            reelingIn = False;
            casted = False;
            inputTime = time.time(); 
            runningAutoFish = True;
        elif (runningAutoFish):
            # Ensure mouse does not have problems
            if (reelingIn):
                mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
            # Assume casted out
            else:
                mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
            runningAutoFish = False;
    elif (not keyboard.is_pressed("g") and togglePressed):
        togglePressed = False;

    if (not runningAutoFish):
        continue;

    screen = cv2.cvtColor(screenCam.get_latest_frame(), cv2.COLOR_RGB2GRAY);

    catchResults = cv2.matchTemplate(screen, imgCatch, cv2.TM_SQDIFF_NORMED);
    catchResult = cv2.minMaxLoc(catchResults)[0] < 0.01;

    pullResults = cv2.matchTemplate(screen, imgPull, cv2.TM_SQDIFF_NORMED);
    pullResult = cv2.minMaxLoc(pullResults)[0] < 0.05;

    stopPullResults = cv2.matchTemplate(screen, imgStopPull, cv2.TM_SQDIFF_NORMED);
    stopPullResult = cv2.minMaxLoc(stopPullResults)[0] < 0.09;

    # Logic

    # Click to pull in fish and latch pullingThing
    if (catchResult and not catching):
        mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
        catching = True;
    
    # Unlatch pullingThing when catch picture is gone and recast
    if (not catchResult and catching):
        mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
        catching = False;

    # Update press mouse when fish orange
    if (pullResult and not reelingIn):
        mouse.press(int(screenWidth/2), int(screenHeight/2), button=2);
        inputTime = time.time();
        casted = False;
        reelingIn = True;
    # Update release mouse press when fish red
    elif (stopPullResult and reelingIn):
        mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
        inputTime = time.time();
        casted = False;
        reelingIn = False;
    # If 5 seconds have passed with no update,
    # either caught or failed fish
    elif (time.time() > inputTime + 5 and not casted):
        mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
        inputTime = time.time();
        casted = True;
