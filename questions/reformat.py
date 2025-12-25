import re

input = open("in.txt", "r+", encoding="UTF-8").read().splitlines()
output = open("out.txt", "w+", encoding="UTF-8")

qnum = 1
extra = "\n"
for i, l in enumerate(input):

    if "feedback" in l:
        continue
    if l == "Feedback":
        if re.findall("\w", input[i+1]):
            l = "\n-Info-"
        else:
            continue

    if len(l) > 100 and re.findall("^Question \d+", input[i-1]):
        broken_line = []
        for j in range(0, len(l), 100):
            broken_line.append(l[j:min(len(l), j+100)])
        print(broken_line)
        l = "\n".join(broken_line)

    if re.findall("^Question \d+", l):
        l = f"\n==============\nQUESTION {qnum}\n=============="
        qnum += 1

    # l is not a answer status
    if l != "Selected" and l != "Unselected":
        output.write((l + extra))
        extra = "\n"
    else:
        # l is an answer status
        whitespace = ["\t-" for i in range( max(
            int( (167-len(input[i+1])) /4),
            0))]
        extra = "".join(whitespace)
        if l == "Selected":
            extra += " [✔] CORRECT"
        if l == "Unselected":
            extra += " [✘] INCORRECT"
