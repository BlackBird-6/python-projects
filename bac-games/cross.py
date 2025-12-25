import re
import time

crosswords = open("Text/cross.txt", "r+").read().splitlines()
minewords = open("Text/mc.txt", "r+").read().splitlines()
advwords = open("Text/advs.txt", "r+").read().splitlines()

f = []
f += crosswords
f += minewords
f += advwords

print("Welcome!"
      "\nType your query. Letters represent single letters. Square brackets denote multiple letters e.g. [eg]"
      "\nUse . to denote any character. [ ] to force a spacebar into the search, useful for finding"
      "\nstarts and ends of workable phrases. ex. We want a word that starts E, blank, blank, any vowel, L"
      "\nthen we use the query [ ]E..[aeiou]l. which returns, for example, [EXPEL]liarmus!"
      "\nType 'reset' to reduce the search to only advancement name/description pairs"
      "\nAfter typing 'reset' type 'minewords' to add all mc items and blocks) or type 'advwords' to add every acronym"
      "\nHave fun!")

while True:

    # Prompt settings
    reg = input("Enter prompt: ")
    if reg == 'minewords':
        f += minewords
    if reg == 'advwords':
        f += advwords
    if reg == 'reset':
        f = []
        f += crosswords
        print("Set")

    if reg == 'exit':
        break

    # Reformat regular expression
    new_reg = []
    in_braces = False
    for c in reg:
        if c == "[":
            in_braces = True
        if c == "]":
            in_braces = False

        if c == ".":
            new_reg.append("[^ ,]")
        elif c.lower() in "abcdefghijklmnopqrstuvwxyz":
            if in_braces:
                new_reg.append(f"{c.lower()}{c.upper()}")
            else:
                new_reg.append(f"[{c.lower()}{c.upper()}]")
        else:
            new_reg.append(c)

        if not in_braces:
            new_reg.append("\s?")

    new_reg = ''.join(new_reg)

    # print(new_reg)

    # Get search results
    res = []
    for l in f:
        l = " " + l
        l = l.replace("\t", "      ")
        l = l.replace("_", "           ")

        search = re.findall(new_reg, l)

        l = l.replace("           ", "")

        if search:
            for query in search:
                l = l.replace(query, "[[[" + query.upper() + "]]]")
            res.append((search, l))

    for l in res:
        print(l)

print(",".join(res)) # Print, repeat ad infinitum

# advs = open("./Text/advs.txt", "r+").read().splitlines()
# res = []
# for a in advs:
#     res.append(("".join([w[0] for w in a.split()]), a))
# for acr, adv in res:
#     print(f"{acr} - (from {"_".join([c for c in adv])})")
#
# time.sleep(100)


# for i, l in enumerate(f):
#     res.append(re.findall('\((.+)\)', l)[-1])
#
# for l in res:
#     print(l)

#     for l in f:
#         stdl = l # standardized
#         stdl = stdl.replace("\t", "_______")
#
#         spaces = [i for i, c in enumerate(stdl) if c == " "]
#         stdl = stdl.replace(" ", "")
#
#         commas = [i for i, c in enumerate(stdl) if c == ","]
#         stdl = stdl.replace(",", "")
#
#         search = re.findall(reg, stdl)
#
#         if search:
#             fl = stdl
#             for i, query in enumerate(search):
#                 fl = fl.replace(query, f"{i}"*len(query))
#             fl = [c for c in fl]
#             for s in commas:
#                 fl.insert(s, ",")
#             for s in spaces:
#                 fl.insert(s, " ")
#             fl = "".join(fl)
#             for i, query in enumerate(search):
#                 fl = re.replace(f"[{i} ]", f"[[[{query.upper()}]]]")
#             res.append((search, fl))
# Word shared in the descriptions of Pixel Perfect, Ten Thousand Blocks, Splatfest, On a Rail, and others