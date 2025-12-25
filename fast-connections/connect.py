import pyautogui
import keyboard
import time
import pyperclip

input = open("in.txt", "r+").read().splitlines()

# class Category:
#     name:

time.sleep(4)

for l in input:
    if("WEEK ") in l:
        continue
    l = l.replace("-- ", "")
    category, members = l.split(":")
    category = category.strip()

    members = members.split(",")
    members = [m.strip() for m in members]

    print(category, members)
    pyautogui.hotkey('ctrl', 'a')
    pyperclip.copy(category)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyperclip.copy(",".join(members))
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab')
    pyautogui.press('tab')



# -- WEEK 25:
# -- Advancements with (missing) periods: Mr Bean, Ladder Climbers Inc, Poseidon vs Hades, D B Copper
# -- Dual Criteria: Chartreuse!, True Cow Tipper, Knocking your socks off, Failed concoctions
# -- Advs with no title case: Where are all your clothes?, You can't take the sky from me, It's a cactus!, I yearned for the mines
# -- G.O.A.T.: whatever floats your goat, riddle me this, goat simulator, gratest of all time