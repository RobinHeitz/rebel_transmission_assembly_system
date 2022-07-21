from threading import Thread, Lock
import time



def add_to_var():
    while True:
        global myVar
        with lock:
            myVar += 1
        time.sleep(.2)


if __name__ == "__main__":

    myVar = 0
    lock = Lock()

    t = Thread(target=add_to_var, daemon=True)
    t.start()

    while True:
        
        time.sleep(2)
        print(myVar)










