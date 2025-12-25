import re

f = open("Text/profiler.txt", "r+").read().splitlines()

res = []
for l in f:
    query = re.findall('.+/(\d.\d\d%)', l)

    if not query:
        continue

    if "prepare" in l:
        continue

    if "execute execute" in l:
        continue

    # if "tag" not in l:
    #     continue

    res.append((l, query))

res.sort(key=lambda h: h[1], reverse=True)

# for l in res:
#     print(l)
print("\n".join([l[0] for l in res]))

with open("Text/profiler_out.txt", "w+") as o:
    for l in res:
        o.write(l[0])
        o.write("\n")

    # if not query and re.findall('.+/(.+%)', l):
    #     print(l, query)

