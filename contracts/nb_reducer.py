def f(o, shard_num):
    state = o[shard_num][0]
    # print(state)
    ret = []
    for elm in state:
        ret.append(reducer(elm))
    # print(ret)
    return ret

def reducer(elm):
    key = list(elm.keys())[0]
    return {key: sum(elm[key])}