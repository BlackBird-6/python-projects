# Instructions for use:
# Press "ALT and =" to increment "That is the fundamental idea"
# Press "ALT and -" to decrement "That is the fundamental idea" (if you make a mistake)
# Press "ALT and ]" to increment "Am I clear"
# Press "ALT and [" to decrement "Am I clear"
# Press "ALT and )" to increment "am I saying it right..?"
# Press "ALT and (" to decrement "am I saying it right..?"
# Press "ALT and `" to end session  (that's the backtick on the top left of the keyboard)
# It will automatically do this 70 minutes after start
# (Data will NOT be saved if you stop the program manually (unless you copy-paste the console data yourself)
# Have fun!

from collections import deque

import keyboard
import time

idea = 0
clear = 0
right = 0
questions = 0
time_start = time.time()

def get_date() -> str:
    time_str = time.localtime(time.time())
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    return months[time_str.tm_mon-1] + " " + str(time_str.tm_mday)


event_queue = []

def get_timestamp() -> str:
    time_str = time.localtime(time.time())
    hour, min, sec = str(time_str.tm_hour), str(time_str.tm_min), str(time_str.tm_sec)
    if len(min) == 1:
       min = "0" + min
    if len(sec) == 1:
       sec = "0" + sec

    return f"[{hour}:{min}:{sec}]"


def fundamental_idea(n: int):
    global idea
    idea += n
    print(f"{get_timestamp()} That is the fundamental idea... #{idea}")
    event_queue.append(f"{get_timestamp()} That is the fundamental idea... #{idea}")
    
def am_i_clear(n: int):
    global clear
    clear += n
    print(f"{get_timestamp()} Am I CLEAR???? #{clear}")
    event_queue.append(f"{get_timestamp()} Am I CLEAR???? #{clear}")

def am_i_saying_it_right(n: int):
    global right
    right += n
    print(f"{get_timestamp()} am I saying it right...?? #{right}")
    event_queue.append(f"{get_timestamp()} am I saying it right...?? #{right}")

def questions(n: int):
    global questions
    questions += n
    print(f"{get_timestamp()} ANY QUESTION???? #{questions}")
    event_queue.append(f"{get_timestamp()} ANY QUESTION???? #{questions}")

# 12/3 NOT CLEAR.

keyboard.add_hotkey('alt+=', fundamental_idea, [1])
keyboard.add_hotkey('alt+-', fundamental_idea, [-1])

keyboard.add_hotkey('alt+]', am_i_clear, [1])
keyboard.add_hotkey('alt+[', am_i_clear, [-1])

keyboard.add_hotkey('alt+0', am_i_saying_it_right, [1])
keyboard.add_hotkey('alt+9', am_i_saying_it_right, [-1])

keyboard.add_hotkey('alt+8', questions, [1])
keyboard.add_hotkey('alt+7', questions, [-1])

halt = False

def end_session():
    global halt
    halt = True

keyboard.add_hotkey('alt+`', end_session)

while True:
    if halt or time.time() - time_start > 60*70: # Stop after 70 minutes
        break
    time.sleep(0.01)

event_queue.insert(0, "\nBegin Session " + get_date())
print(get_date())

f = open("out.txt", "a")
for e in event_queue:
    f.write(e + "\n")
f.close()