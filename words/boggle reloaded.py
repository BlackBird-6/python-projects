import pyautogui
import time

str = "e"
print(str + "a")

# input = input("What grid would you like to input? ").split("/")
input = "XYHWITSIIN/CELNSECNDS/EYGUIROTTE/TLASPNEITX/SBTHCATUTJ/OILICHLCIO/INROTALANC/TYAKUYRLTD/IULNTERIZE/XENOVEQUSA".split("/")

grid = [[c for c in l] for l in input]
print(grid)

words = open("pythonProject\words\more_words.txt", "r+").read().splitlines()
res = []

neis = [[-1, 1], [-1, 0], [-1, -1], [1, 0], [1, -1], [1, 1], [0, 1], [0, -1]]
ROWS = len(grid)
COLUMNS = len(grid[0])

def dfs(r, c, remaining, seen, word):
    for dr, dc in neis:
        R, C = r+dr, c+dc

        if R < 0 or R >= ROWS or C < 0 or C >= COLUMNS:
            continue

        if (R, C) in seen:
            continue

        if grid[R][C] == remaining[0]:
            if len(remaining) == 1:
                res.append(word)
                return
            dfs(R, C, remaining[1:], seen + [(R, C)], word)

for word in words:
    word = word.upper()

    if len(word) <= 3:
        continue

    seen = []

    for r in range(ROWS):
        for c in range(COLUMNS):
            if grid[r][c] == word[0]:
                dfs(r, c, word[1:], [(r, c)], word)

# remove dupes
res = list(set(res))
res.sort(key=lambda s: len(s), reverse=True)
print(res)
print(len(res))

time.sleep(3)
for r in res:
    pyautogui.write(r)
    pyautogui.press('enter')
    pyautogui.press('esc')