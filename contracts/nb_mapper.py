import os
def f(o, shard_num):
    s = read_file(shard_num)
    # print(s)
    label_index = 8
    ret = {}
    for il, line in enumerate(s):
        if line:
            vals = line.split(",")
            label = vals[label_index]
            for iv, val in enumerate(vals):
                if iv == label_index:
                    continue
                tup = "%s,%s,%s" % (iv, val, label)
                if tup in ret:
                    ret[tup] += 1
                else:
                    ret[tup] = 1
    return ret


def read_file(shard_num, num_shards=3):
    if "nb_data_loc" in os.environ:
        with open(os.environ["nb_data_loc"], "r") as f:
            s = f.read().split("\n")
        l = len(s)
        return s[shard_num * l // num_shards:(shard_num + 1) * l // num_shards]
    else:
        print("!!!!!!!!!!!!!!!!!!!!env not set !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# print(f(0, 0))
