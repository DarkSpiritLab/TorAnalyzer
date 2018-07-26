# send and receive  client work
# "clientReceive" -> {"url":"xxx.onio","level":"1,2,3,4,5","num":10}
# "clientEnd" -> {"url":"xxx.onio","state":"end"}
# "clientResult" <-  {"ip":localIP,"url":workList["url"],"level":workList["level"]}
# !/usr/bin/python
# -*- coding: UTF-8 -*
import sys
from os import path

sys.path.append(path.split(path.split(path.abspath(__file__))[0])[0])

import json
import random
import time

from Pub.RabbitMQ import RabbitMQWrapper

from Pub.ORM import Url, sessionmaker, engine

'''
{"url":url,"url_id":url_id, "level": self.level, "request_id":random.randint(0,100000000)}
'''

queueStartName = "clientReceive"
queueTask="clientTask"
class ClientWork:
    def sendTask(self, url, num = 10, level = "1"):
        lastUrl = ""
        number = 30  # receive same work tell number
        session = self.Session()
        u = session.query(Url).filter_by(url = url).first()
        url_id = 0

        if (u is None):
            u = Url(url = url)
            session.add(u)
            session.commit()
            # todo check u contains url_id
        url_id = u.url_id

        for i in range(num):
            infor = {"url": url, "url_id": url_id, "level": self.level, "request_id": random.randint(0, 100000000)}
            body = json.dumps(infor)
            if(self.sendChannel.is_closed):
                self.sendChannel=self.rabbitMQ.getChannel()
                self.sendChannel.queue_declare(queue = queueTask)
            self.sendChannel.basic_publish(exchange = '', routing_key = queueTask, body = body)
    def start(self):
        for method_fram, properties, body in self.receiveChannel.consume(queueStartName):
            # try:
            task = json.loads(body.decode("utf8"))
            self.sendTask(task["url"],task["num"],task["level"])

    def __init__(self):
        self.Session = sessionmaker(engine)
        self.rabbitMQ = RabbitMQWrapper()
        self.sendChannel = self.rabbitMQ.getChannel()
        self.sendChannel.queue_declare(queue = queueTask)
        self.receiveChannel=self.rabbitMQ.getChannel()
        self.receiveChannel.queue_declare(queue = queueStartName)
        self.receiveChannel.basic_qos(prefetch_count = 1)

if  __name__=="__main__":
    pass
    #ClientWork().sendTask("6gi7ufqbqnllbbvx.onion",10)
