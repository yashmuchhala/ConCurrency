def f(o, shard_num):
    with open("rnd0.txt", "r") as f:
        s = f.read()
        interval = len(s) // len(o)
        start = shard_num * interval
        end = start + interval
        ret = {}
        for ch in s[start:end]:
            if ch in ret:
                ret[ch] += 1
            else:
                ret[ch] = 1
    return ret
