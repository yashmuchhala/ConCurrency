import json


def f(o, shard_num):
    interval = 10 ** 5
    a = shard_num * interval
    b = a + interval
    ret = []
    for i in range(a, b + 1):
        if (i == 1):
            continue
        flag = 1
        for j in range(2, i // 2 + 1):
            if (i % j == 0):
                flag = 0
                break
        if flag == 1:
            ret.append(i)
    # return "%s to %s, there are %s primes" % (a, b, len(ret))
    return len(ret)


import time

s = time.time()
ans = f(0, 0)
ans += f(0, 1)
# print(time.time() - s)
# print(len(ans))
ans += f(0, 1)
print(time.time() - s, ans)
# print(len(ans))
