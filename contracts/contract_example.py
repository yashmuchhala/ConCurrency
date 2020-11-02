import time
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

def f(o, shard_num):
    ret = 0
    for i in range(shard_num * 10 ** 7, (shard_num + 1) * 10 ** 7):
        ret += i
    return ret


# start = time.time()
# print(f(0, 0))
# print(f(0, 1))
# time.time() - start
#
# print("contr")
