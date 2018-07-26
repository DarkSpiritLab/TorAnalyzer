#!/usr/bin/python3
# -*- coding: UTF-8 -*

# "clientReceive" -> {"url":"xxx.onio","level":"1,2,3,4,5","num":10}
# "clientEnd" -> {"url":"xxx.onio","state":False}
# "clientResult" <-  {"ip":localIP,"url":workList["url"],"level":workList["level"]}
import json
import time
import urllib
import sys
import subprocess
from os import path
sys.path.append(path.split(path.split(path.abspath(__file__))[0])[0])

from urllib import request


from Client.Relay.handleLocalRelaysInfo import LocalRelayInfoHandler
from Pub.RabbitMQ import RabbitMQInfo, RabbitMQWrapper
from Pub.myutil import get_host_ip

rmq= RabbitMQInfo()


httpAgent = 'http://127.0.0.1:9011/'
queueName = "clientTask"

class Client():
    def __init__(self):
        self.rabbitMQ=RabbitMQWrapper()
        self.localIP = get_host_ip()


    # def sendResult(self,work):
    #     work["my_ip"]=self.localIP
    #     result=work
    #     infor = json.dumps(result)
    #     self.channel.basic_publish(exchange='', routing_key=queueResult, body=infor)
    #     print("sendResult "+infor)


    def receiveEnd(self):
        pass

    def runWork(self,work):
        print("runWork start")
        self.startTor()
        self.writeTaskIntoFile(work["request_id"],work["url_id"])
        url = work["url"]
        if not url.startswith("http"):
            url = "http://"+url
        try:
            proxy_handler = urllib.request.ProxyHandler({'http': httpAgent})
            opener = urllib.request.build_opener(proxy_handler)
            opener.open(url)
            self.sendResult(work)
            print("Success: "+url)
        except:
            print("Fail: "+url)
        print("runWork end")
        #stop tor after finishing this request
        self.stopTor()

    def stopTor(self):
        self.p.kill()

    def startTor(self):
        args=['/tor_release/tor', '-f', '/config/torrc']
        self.p=subprocess.Popen(args = args)
        time.sleep(3)
        pass

    def receiveWork(self):
        print("receiveWork start")
        channel=self.rabbitMQ.getChannel()
        channel.queue_declare(queue=queueName)
        channel.basic_qos(prefetch_count=1)
        lastUrl = ""
        number = 30  # receive same work tell number
        for method_fram,properties,body in channel.consume(queueName):
            # try:
            result = json.loads(body.decode("utf8"))
            channel.basic_ack(delivery_tag = method_fram.delivery_tag)
            if lastUrl == result["url"]:
                number-=1
                if number !=0:
                    time.sleep(1)
                    continue
            number = 30
            lastUrl = result["url"]
            print("Receive client work: " + body.decode("utf8"))
            self.runWork(result)
            # except:
            #     print("Failed to receive work")
        requeued_messages = channel.cancle()
        print('Requeued %i messages' %requeued_messages)
        print("receiveWork end")

    def writeTaskIntoFile(self,request_id,url_id):
        with open("./currentTask","w+") as f:
            f.writelines(str(request_id)+"\n")
            f.writelines(str(url_id))
        return


if __name__ == "__main__":
    print("client start")
    LocalRelayInfoHandler().startHandleLocalRelaysInfo()
    print("client start receive remote task")
    Client().receiveWork()