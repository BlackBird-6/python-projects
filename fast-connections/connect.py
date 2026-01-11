import pyautogui
import keyboard
import time
import pyperclip

input = open("in.txt", "r+", encoding="UTF-8").read().splitlines()

def paste(msg):
    pyautogui.hotkey('ctrl', 'a')
    pyperclip.copy(msg)
    pyautogui.hotkey('ctrl', 'v')

time.sleep(4)

for l in input:
    l = l.replace("-- ", "")

    # Line 1
    if("BACAP Connections") in l:
        paste(l)
        pyautogui.press('tab')
        paste("BlackBird_6")
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        continue

    category, members = l.split(":")
    category = category.strip()

    members = members.split(",")
    members = [m.strip() for m in members]

    print(category, members)
    paste(category)
    pyautogui.press('tab')

    paste(",".join(members))
    pyautogui.press('tab')
    pyautogui.press('tab')



# -- WEEK 25:
# -- Advancements with (missing) periods: Mr Bean, Ladder Climbers Inc, Poseidon vs Hades, D B Copper
# -- Dual Criteria: Chartreuse!, True Cow Tipper, Knocking your socks off, Failed concoctions
# -- Advs with no title case: Where are all your clothes?, You can't take the sky from me, It's a cactus!, I yearned for the mines
# -- G.O.A.T.: whatever floats your goat, riddle me this, goat simulator, gratest of all time