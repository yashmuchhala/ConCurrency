import time, os
def read_file():
    with open(os.environ["nb_data_loc"], "r") as f:
        s = f.read().split("\n")
    return s

def f():
    start = time.time()
    s = read_file()
    print(time.time() - start)
    # print(s)
    label_index = 8
    ret = {}
    for il, line in enumerate(s):
        if line:
            vals = line.split(",")
            # print(il)
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
s=time.time()
for i in range(1):
    f()
print(time.time()-s)