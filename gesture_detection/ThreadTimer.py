import threading
import time

cout=0
def recalibrate():
    threading.Timer(5.0, recalibrate).start()#after 5 second, run function
    global cout
    cout=cout+1
    print (cout)

recalibrate()
#continue rest of the operation 
for i in range(15):
    time.sleep(2)
    print("ahaha")