import cv2;
import numpy as np;
import pyautogui;
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

# Setup variables for pulling in fish
mouse = PyMouse();
screenWidth, screenHeight = mouse.screen_size();
pullingThing = False; # Used to lock for duration of pulling in
pullingFish = False;

# For now loop forever
while True:
    # Take one screenshot and format for cv2
    screen = pyautogui.screenshot();
    screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY);

    # Check if catch is on screen
    catchOnScreen = cv2.matchTemplate(screen, imgCatch, cv2.TM_SQDIFF_NORMED);
    catchOnScreen = cv2.minMaxLoc(catchOnScreen)[0] < 0.1;

    # Check if pull is on screen
    pullOnScreen = cv2.matchTemplate(screen, imgPull, cv2.TM_SQDIFF_NORMED);
    pullOnScreen = cv2.minMaxLoc(pullOnScreen)[0] < 0.1

    # Check if stop pull is on screen
    stopPullOnScreen = cv2.matchTemplate(screen, imgStopPull, cv2.TM_SQDIFF_NORMED);
    stopPullOnScreen = cv2.minMaxLoc(stopPullOnScreen)[0] > 0.1;

    ####################################
    # Logic to control mouse inputs
    # based on images found
    ####################################

    # Unlatch pullingThing when catch picture is gone
    if (not catchOnScreen and pullingThing):
        pullingThing = False;

    # Click to pull in fish and latch pullingThing
    if (catchOnScreen and not pullingThing):
        mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
        pullingThing = True;
    
    # Update mouse press for pulling in fish
    if (pullOnScreen and not pullingFish):
        mouse.press(int(screenWidth/2), int(screenHeight/2), button=2);
        pullingFish = True;
    elif (stopPullOnScreen and pullingFish):
        mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
        pullingFish = False;
    # After fish is caught release mouse
    elif (pullingFish and not pullOnScreen and not stopPullOnScreen):
        mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
        pullingFish = False;
