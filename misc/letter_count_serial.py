import time


def f(o, shard_num):
    with open("C:\\Users\\Harshit\\Desktop\\rnd%s.txt" % shard_num, "r") as f:
        s = f.read()
        ret = {}
        for ch in s:
            if ch in ret:
                ret[ch] += 1
            else:
                ret[ch] = 1
    return ret


s = time.time()
d1 = f(0, 0)
d2 = f(0, 1)
d3 = f(0, 2)
r = {}
for key in d1:
    r[key] = d1[key] + d2[key] + d3[key]
print(r)
print(time.time() - s)
