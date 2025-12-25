# print("".join(s[0] for s in input("Input. ").split()))

import matplotlib.pyplot as plt

a = 1
seq = []
for _ in range(1000):
    a = (2*a+4)%234002
    # a = (31 * a + 127) % 147017
    seq.append(a)

plt.plot(seq)
plt.show()