# print("".join(s[0] for s in input("Input. ").split()))

str = "boned"
res = []
def boned(s, rem, i, lastSpace):
    if(rem == 0):
        res.append("".join(s))
    else:
        if not lastSpace:
            boned(s + [" "], rem-1, i,True)
        boned(s + [str[i%5]], rem-1, i+1,False)

boned([], 14, 0, False)
print(len(res))
output = ",".join(res)
print(output)
print(len(output))

# res = []
# for i in range(32):
#     s = []
#     for j in range(i):
#         s.append(str[j%5])
#     res.append("".join(s))
# print(res)
# import matplotlib.pyplot as plt
#
# a = 1
# seq = []
# for _ in range(1000):
#     a = (2*a+4)%234002
#     # a = (31 * a + 127) % 147017
#     seq.append(a)
#
# plt.plot(seq)
# plt.show()