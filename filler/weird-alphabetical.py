from collections import defaultdict

remap = defaultdict(int)

new_alphabet = "qazwsxedcrfvtgbyhnujmikolp"
words = open("Text/words.txt", "r+").read().splitlines()

for i, c in enumerate(new_alphabet):
    remap[c] = i

transformed = {}
for w in words:
    transformed[w] = [remap[c.lower()] for c in w]

words.sort(key=lambda w: transformed[w])
print(transformed)
print(words)


