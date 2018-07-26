import sys
from os import path
import time
from threading import Thread
sys.path.append(path.split(path.split(path.abspath(__file__))[0])[0])
from Server.handleConnInfoQueue import RealysMessageHandler
def startHanderMessage():
    handler=RealysMessageHandler()
    while(True):
        handler.startReceive()
        time.time()
if __name__=="__main__":
    t1=Thread(target = startHanderMessage)
    t1.start()
    t1.join()