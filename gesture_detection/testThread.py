import threading

cout=0

def printit():
    while True:
        global cout
        cout=cout+1
        print (cout)
    # threading.Timer(1.0, printit).start()
    #  ^ why you need this? However it works with it too

threading.Timer(20.0,printit).start()