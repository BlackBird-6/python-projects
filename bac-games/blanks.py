import sqlite3
import random
import numpy as np

conn = sqlite3.connect('../bac-database/bacap.db')
cursor = conn.cursor()
database_data = cursor.execute('''SELECT name from advancements ''')
# database_data = cursor.execute('''SELECT name from advancements WHERE version like '%1.20%' OR version like '%1.19%' OR version like '%1.18%' OR version like '%1.17%' OR version like '%1.16%' ''')
d = database_data.fetchall()
advs = [adv[0] for adv in d]
print(advs)

# CREATE FILL IN THE BLANKS
advs = [adv for adv in advs if len(adv) > 10]
candidates = []

NUM_ANSWERS = 200
START_REVEAL_PERCENT = 80
END_REVEAL_PERCENT = 30

while len(candidates) < NUM_ANSWERS:
    candidates.append(advs.pop(random.randrange(0, len(advs))))
for i, adv in enumerate(candidates):
    # 30 to 80
    num_chars = len([c for c in adv if c in "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"])
    NUM_REVEALS = np.floor(num_chars *
           (START_REVEAL_PERCENT - (START_REVEAL_PERCENT-END_REVEAL_PERCENT) * i/NUM_ANSWERS ) /100)
    # print(adv, NUM_REVEALS)
    count = 0
    filtered_adv = [("_" if c in "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    else c) for c in adv]
    while count < NUM_REVEALS:
        index = random.randrange(0, len(filtered_adv))
        if(filtered_adv[index] == "_"):
            count += 1
            filtered_adv[index] = adv[index]

    filtered_adv = "".join(filtered_adv)
    filtered_adv = filtered_adv.replace("…", "...")
    filtered_adv = filtered_adv.replace("<", "")

    print(f"{filtered_adv}\t                                                                                                              {adv}")

print(advs)
# print(len(advs))
# print("DONE")