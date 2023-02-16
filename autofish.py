import dxcam;
import cv2;
import os.path;
from pymouse import PyMouse;
import time;
import keyboard;

#Setup simple toggle key for auto fishing
toggleKey = 'g';

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

# Ensure all neccesary images can be loaded
if (not os.path.exists(imgCatch)):
    raise Exception("Image file(s) not found");

# Load actual images
imgCatch = cv2.imread(imgCatch, cv2.IMREAD_GRAYSCALE);

# Setup for mouse input
mouse = PyMouse();
screenWidth, screenHeight = mouse.screen_size();

# Start screen recording
screenCam = dxcam.create(output_color="GRAY");
screenCam.start(target_fps=60);

# Vars for state logic
state = State.DISABLED;
fishingIdleTime = time.time(); # Used to recast after fish is caught (or failed)

while (True):
    # Check to enable or disable
    if (keyboard.is_pressed(toggleKey)):
        if (state == State.DISABLED):
            state = State.IDLE;
            time.sleep(2);
        else:
            keyboard.press_and_release('s');
            state = state.DISABLED;
            time.sleep(2);

    # Get latest screen image
    screen = screenCam.get_latest_frame();

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
                keyboard.press_and_release('s');
                state = State.IDLE;
                time.sleep(0.5);

