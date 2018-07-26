import sys
from os import path
import time
from threading import Thread
sys.path.append(path.split(path.split(path.abspath(__file__))[0])[0])
from Server.handleConnInfoQueue import RealysMessageHandler
from Server.sendTask import ClientWork
def startHanderMessage():
    handler=RealysMessageHandler()
    while(True):
        handler.startReceive()
        time.sleep(1)

def sendClientTask():
    c=ClientWork()
    c.start()

if __name__=="__main__":
    t1=Thread(target = startHanderMessage)
    t1.start()
    t2=Thread(target = sendClientTask)
    t1.join()
    t2.join()