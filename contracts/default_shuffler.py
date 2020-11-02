def f(o, shard_num):
    num_shards = len(o)
    joined_state = {}
    for elm in o:
        elm = elm[0]
        for key in elm.keys():
            if key in joined_state:
                joined_state[key].append(elm[key])
            else:
                joined_state[key] = [elm[key], ]
    joined_keys = sorted(joined_state.keys())
    num_keys = len(joined_keys)
    keys_per_shard = int(num_keys / num_shards)
    ret = []
    if shard_num == num_shards - 1:
        for key in joined_keys[keys_per_shard * shard_num:]:
            ret.append({key: joined_state[key]})
    else:
        for key in joined_keys[keys_per_shard * shard_num:keys_per_shard * (shard_num + 1)]:
            ret.append({key: joined_state[key]})
    print(joined_state, joined_keys, ret)
    return ret
