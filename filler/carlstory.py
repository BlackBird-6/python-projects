import re
f = open("./Text/carlstory.txt", "r+").read().splitlines()

for i, l in enumerate(f):
    if i%10 == 0:
        l = l.replace("â€™", "'")
        res = re.sub("\(.+\)", "", l)
        print(f"{l}{f"/{res}" if l.replace("(", "") != l else ""}")