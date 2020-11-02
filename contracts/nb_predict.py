s = input("Enter trained parameters\n")
l = eval(s)
reducer_result = []
for elm in l:
    for e in elm[0]:
        reducer_result.append(e)

classes = ["L", "B", "R"]
k_index = 1

n_classes = {}
tot = 0
for i, cls in enumerate(classes):
    ncls = 0
    for res in reducer_result:
        key = list(res.keys())[0]
        val = res[key]
        key = key.split(",")
        if int(key[0]) == k_index and key[2] == cls:
            ncls += val
    n_classes[cls] = ncls
    tot += ncls

merged_reducer_result = {}
for res in reducer_result:
    key = list(res.keys())[0]
    val = res[key]
    merged_reducer_result[key] = val

while True:
    features = input("Enter features, comma separated\n").split(",")
    prods = []
    for cls in classes:
        prod = n_classes[cls] / tot
        for i, feature in enumerate(features):
            prod *= merged_reducer_result["%s,%s,%s" % (i, feature, cls)]/n_classes[cls]
        print(cls, prod)
        prods.append(prod)
    s = sum(prods)
    print("----------------------")
    for prod, cls in zip(prods, classes):
        print(cls, prod/s)
