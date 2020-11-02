import random
import time

if __name__ == '__main__':
    # num = int(input()
    start = time.time()
    num = 10 ** 8
    s = "abcdefghijklmnopqrstuvwxyz"
    ret = []
    for i in range(num):
        ret.append(random.choice(s))
        if i % 10**8 == 0:
            print(i)
        if i % 10 == 0:
            ret.append("\n")
    # print("".join(ret))
    with open("lettercount0.txt", "w") as f:
        f.write("".join(ret))
    print(time.time() - start)
