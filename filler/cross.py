import re
import time

crosswords = open("./Text/cross.txt", "r+").read().splitlines()
minewords = open("./Text/mc.txt", "r+").read().splitlines()
advwords = open("./Text/advs.txt", "r+").read().splitlines()

f = crosswords
f += minewords
f += advwords

# ex c.i..[ ]
while True:
    reg = input("Enter prompt: ")
    if reg == 'minewords':
        f += minewords
    if reg == 'advwords':
        f += advwords
    if reg == 'reset':
        f = crosswords

    if reg == 'exit':
        break

    res = []
    for l in f:
        l = " " + l
        l = l.replace("\t", "      ")
        l = l.replace("_", "           ")
        new_reg = []
        no_spaces = True
        for c in reg:
            if c == "[":
                no_spaces = True
            if c == "]":
                no_spaces = False

            if c == ".":
                new_reg.append("[^ ,]")
            elif c.lower() in "abcdefghijklmnopqrstuvwxyz":
                new_reg.append(f"[{c.lower()}{c.upper()}]")
            else:
                new_reg.append(c)

            if not no_spaces:
                new_reg.append("\s?")

        new_reg = ''.join(new_reg)

        # print(new_reg)
        search = re.findall(new_reg, l)

        l = l.replace("           ", "")

        if search:
            for query in search:
                l = l.replace(query, "[[[" + query.upper() + "]]]")


            res.append((search, l))

    for l in res:
        print(l)

print(",".join(res))

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