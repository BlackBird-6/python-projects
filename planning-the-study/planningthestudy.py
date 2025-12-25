import pyautogui
import pytesseract
from PIL import ImageGrab
from pyautogui import click
from pynput.mouse import Listener
import pynput.keyboard
import pyautogui
import time

# Change to installation path for Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

emergency_stop = False
# Emergency stop
def on_press(key):
    global emergency_stop
    try:
        if key.char == 'z':
            emergency_stop = True
    except AttributeError:
        pass

# Start the listener in a separate thread
z_listener = pynput.keyboard.Listener(on_press=on_press)
z_listener.start()

coords = []
while True:

    choice = ""
    while choice.lower() != "n" and choice.lower() != "y":
        choice = input("Change detection coordinates? (Y/N) ")

    if choice.lower() == "n":
        break

    # Ready position
    print("Click detection will activate in three seconds, get ready...")
    time.sleep(3)

    def on_click(x, y, button, pressed):
        if pressed:
            coords.append(int(x))  # Store click coordinates
            coords.append(int(y))
            print(f"Click {int(len(coords)/2)}: ({int(x)}, {int(y)})")

            if len(coords) == 6:  # Stop after two clicks
                return False  # Stop listener

    # Start listening for mouse clicks
    print("Click three times anywhere on the screen...")
    print("Click 1 and 2 is the bounding box to capture text (top left & bottom right)")
    print("Click 3 is the position to click to refresh the question.")

    with Listener(on_click=on_click) as listener:
        listener.join()

    print(f"\nCaptured Coordinates: {coords}")

    write_coords = open("coords.txt", "w+")
    for c in coords:
        write_coords.write(str(c) + "\n")
    write_coords.close()

coords = [int(c) for c in open("coords.txt", "r+").read().splitlines()]

screenshot_coords = coords[:4]
click_coords = coords[4:]

while True:
    print("\nWrite all necessary inputs that you want to detect. Separate queries with \"/\"")
    print("For example: \"6/(12, 0)/9x\"")
    queries = input()
    queries.replace(" ", "")
    # queries = "6/(12, 0)"
    # queries = "6/(12, 0)/(3, 3)"
    queries = queries.split("/")

    print("Initiating in three seconds...")
    print("Tip: You can press 'Z' to cancel the search operation.\n")
    print(screenshot_coords, click_coords)
    time.sleep(3)

    while True:
        image = ImageGrab.grab(bbox=screenshot_coords)
        image.save("math.png")
        image_text = pytesseract.image_to_string("math.png").replace(" ", "")
        # print(image_text)

        found = True
        for query in queries:

            if query not in image_text:

                # Debug text, uncomment the below lines to show
                image_text = image_text.replace("\n","")
                print(f"{query} not found in {image_text}.")

                found = False
                click(click_coords)
                time.sleep(0.35)
                break

        if emergency_stop:
            print("EMERGENCY STOP")
            emergency_stop = False
            break

        if found:
            break

    print("Found!")


    choice = ""
    while choice.lower() != "y" and choice.lower() != "n":
        choice = input("Choose another query? (Y/N) ")
    if choice.lower() == "n":
        break
print("Farewell")

