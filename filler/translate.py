import re

input = open("Text/lang_in.txt", "r+", encoding='UTF-8').read().splitlines()

letters = [c for c in "abcdefghijklmnopqrstuvwxyz0123456789,.?'!()-:§&;[]%$#_<>\"/"]
morse = ".- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----. --..-- .-.-.- ..--.. .----. -.-.-- -.--. -.--.- -....- ---... § .-... -.-.-. [ ] % $ # ..--.- < > .-..-. /".split()

map = {' ': '/'}
for i in range(len(letters)):
    map[letters[i]] = morse[i]

out = open("Text/lang_out.txt", "w+", encoding='UTF-8')

for l in input:
    if re.findall("\".+?\" ?: ?\"\",", l):
        translate = re.findall("\"(.+?)\" ?:", l)[0]
        translate = translate.replace("’", "'")
        translate = translate.replace("‘", "'")
        translate = translate.replace("“", "\"")
        translate = translate.replace("”", "\"")
        translate = translate.replace("ñ", "n")
        translate = translate.replace("…", "...")

        print(translate)
        translated = " ".join([map[c.lower()] for c in translate])
        print(translated)
        segment = re.findall("(\".+?\" ?: ?\")(\",)", l)[0]
        print(segment)
        out.write(segment[0] + translated + segment[1] + "\n")
    else:
        out.write(l + "\n")