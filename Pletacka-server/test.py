import time

for x in range(10):
    time.sleep(0.5) # shows how its working
    print("\r {}".format(x), end="")