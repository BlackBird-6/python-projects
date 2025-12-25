from collections import Counter

import pyautogui
import time

f = open("more_words.txt", "r+").read().splitlines()

letters = "v e n d o r".split()
res = []

for word in f:
    ok = True
    for l in word:
        if l not in letters:
            ok = False
            continue
    if not ok:
        continue

    c = Counter(word)
    if c['e'] and c['o'] > 0:
        continue

    if len(word) < 3:
        continue

    word = word[::-1]
    if 'dn' in word or 'dr' in word or 'dv' in word or 'nr' in word or 'nv' in word or 'rv' in word:
        continue
    word = word[::-1]
    if 'dn' in word or 'dr' in word or 'dv' in word or 'nr' in word or 'nv' in word or 'rv' in word:
        continue

    res.append(word)

res.sort(key=lambda l: len(l))
print(res)
# letters = "h l t p o a c".split()
# res = []
#
# for word in f:
#     if "p" not in word:
#         continue
#
#     valid = True
#     for c in word:
#         if c not in letters:
#             valid = False
#             break
#     if valid:
#         res.append(word)
#
# res.sort(key=lambda s: len(s), reverse=True)
# print(res)
#
# time.sleep(3)
# for r in res:
#     pyautogui.write(r)
#     pyautogui.press('enter')

## ### #### #####
??? ???XX ???? ??



# DEN EVEN ????N EVENED
# EVENED E?OO? EDE NEVE
#
# D ERRED
#
# VON
# VENDOR
#
# DONOR
# ['dee', 'den', 'don', 'ene', 'ere', 'err', 'eve', 'ned', 'nee', 'nne', 'nod', 'non', 'nor', 'odd', 'ono', 'red', 'rev', 'rod', 'ron', 'dodo', 'even', 'ever', 'odor', 'veer', 'donor', 'erred', 'never', 'deeded', 'evened', 'revere']