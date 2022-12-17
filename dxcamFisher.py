import dxcam;
import cv2;
import os.path;
from pymouse import PyMouse;
import time;
import keyboard;

# Use enum for state tracking
import enum;
class State(enum.Enum):
    DISABLED = 0; # When autofisher is disabled
    IDLE = 1; # Just standing (doing nothing)
    CASTED_OUT = 2; # Fishing pole casted out
    REELING_IN_FISH = 3; # Holding right click to reel in fish
    FISHING_IDLE = 4; # Idle when fish is pulling

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

# Setup for mouse input
mouse = PyMouse();
screenWidth, screenHeight = mouse.screen_size();

# Start screen recording
screenCam = dxcam.create();
screenCam.start(target_fps=60);

# Vars for state logic
state = State.DISABLED;
fishingIdleTime = time.time(); # Used to recast after fish is caught (or failed)

# Add delay for now
time.sleep(3);

while (True):
    # Check to enable or disable
    if (keyboard.is_pressed("g")):
        if (state == State.DISABLED):
            state = State.IDLE;
            time.sleep(2);
        else:
            # Need to release mouse if pulling in fish
            if (state == State.REELING_IN_FISH):
                mouse.release(int(screenWidth/2), int(screenHeight/2), button = 2);
            # Reel in if casted out
            if (state == State.CASTED_OUT):
                mouse.click(int(screenWidth/2), int(screenHeight/2), button = 2);
            state = state.DISABLED;
            time.sleep(2);

    # Get latest screen image
    screen = cv2.cvtColor(screenCam.get_latest_frame(), cv2.COLOR_RGB2GRAY);

    match state:

        case State.IDLE:
            # Cast fishing rod
            mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
            state = State.CASTED_OUT;

        case State.CASTED_OUT:
            # Check for when catching something
            catchResults = cv2.matchTemplate(screen, imgCatch, cv2.TM_SQDIFF_NORMED);
            if (cv2.minMaxLoc(catchResults)[0] < 0.01):
                # If found, reel in
                mouse.click(int(screenWidth/2), int(screenHeight/2), button=2);
                fishingIdleTime = time.time(); 
                state = State.FISHING_IDLE;

        case State.FISHING_IDLE:
            # Check if no longer catching fish
            if (fishingIdleTime + 3.5 < time.time()):
                state = State.IDLE;
            # Check to start reeling in
            pullResults = cv2.matchTemplate(screen, imgPull, cv2.TM_SQDIFF_NORMED);
            if (cv2.minMaxLoc(pullResults)[0] < 0.05):
                mouse.press(int(screenWidth/2), int(screenHeight/2), button=2);
                fishingIdleTime = time.time(); 
                state = State.REELING_IN_FISH;
        
        case State.REELING_IN_FISH:
            # Check if no longer catching fish
            if (fishingIdleTime + 3.5 < time.time()):
                state = State.IDLE;
            # Check to stop reeling in
            stopPullResults = cv2.matchTemplate(screen, imgStopPull, cv2.TM_SQDIFF_NORMED);
            if (cv2.minMaxLoc(stopPullResults)[0] < 0.09):
                mouse.release(int(screenWidth/2), int(screenHeight/2), button=2);
                fishingIdleTime = time.time(); 
                state = State.FISHING_IDLE;