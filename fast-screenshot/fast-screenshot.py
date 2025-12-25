import pyautogui
from PIL import ImageGrab
from pyautogui import click
from pynput.mouse import Listener
import pynput.keyboard
import pyautogui
import time
import winsound

emergency_stop = False
# Emergency stop
def on_press(key):
    global emergency_stop
    try:
        if key.char == 'z':
            emergency_stop = True
    except AttributeError:
        pass

s = "a"
s.strip()


coords = []

i = 0
while True:

    def on_click(x, y, button, pressed):
        global i
        if pressed:
            coords.append(int(x))  # Store click coordinates
            coords.append(int(y))
            print(f"Click {int(len(coords)/2)}: ({int(x)}, {int(y)})")

            if len(coords) % 4 == 0:  # Stop after two clicks
                winsound.Beep(400, 200)
                print(f"\nCaptured Coordinates: {coords[-4:]}")
                try:
                    image = ImageGrab.grab(bbox=tuple(coords[-4:]))
                    i += 1
                    image.save(f"images/screenshot{i}.png")
                except Exception as e:
                    print(e)
            else:
                winsound.Beep(440, 200)


    with Listener(on_click=on_click) as listener:
        listener.join()



