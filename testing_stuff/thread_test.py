from threading import Thread, Lock
import time



def add_to_var():
    while my_flag:
        global myVar
        with lock:
            myVar += 1
        time.sleep(.2)


if __name__ == "__main__":

    myVar = 0

    my_flag = True
    lock = Lock()

    t = Thread(target=add_to_var, daemon=True)
    t.start()
    print(myVar)
    time.sleep(1)
    print(myVar)
    time.sleep(1)
    print(myVar)
    time.sleep(1)
    print(myVar)
    time.sleep(1)

    my_flag = False










