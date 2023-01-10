# CoreFisher
An auto fishing Python script for the game Core Keeper. To use
You must manually start and stop the script.
The script starts in disabled mode, tap toggle (g key by default) to enable and disable auto fishing.

# Requirements To Use
* The script clicks in the middle of the screen, so you must be **directly above** a water source.
* Needs a fishing rod to be equiped when enabling.
* The script requires the game to be fullscreen, and it has only been tested at 1080p.

# Config
The default toggle key to enable auto fishing is g.
If you would like to change it, simply change the toggleKey variable in autofish.py to your desired key.
(toggleKey is directly under the imports).

# Dependencies
* [OpenCV] for image recognition
* [DXCam] for fast screen capture
* [PyUserInput] for simulating mouse input and reading keyboard input

[OpenCV]: <https://pypi.org/project/opencv-python>
[DXCam]: <https://pypi.org/project/dxcam>
[PyUserInput]: <https://pypi.org/project/PyUserInput>
