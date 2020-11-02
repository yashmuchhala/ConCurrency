def f(o, shard_num):
    num_shards = len(o)
    n = 192_000
    interval = n // num_shards
    a = shard_num * interval
    b = a + interval
    ret = []
    for i in range(a, b + 1):
        if i == 1:
            continue
        flag = 1
        for j in range(2, i // 2 + 1):
            if i % j == 0:
                flag = 0
                break
        if flag == 1:
            ret.append(i)
    return {"primes": len(ret)}
