# send and receive  client work
# "clientReceive" -> {"url":"xxx.onio","level":"1,2,3,4,5","num":10}
# "clientEnd" -> {"url":"xxx.onio","state":"end"}
# "clientResult" <-  {"ip":localIP,"url":workList["url"],"level":workList["level"]}
#!/usr/bin/python
# -*- coding: UTF-8 -*
import sys
from os import path
sys.path.append(path.split(path.split(path.abspath(__file__))[0])[0])

import json
import random

from Pub.RabbitMQ import RabbitMQWrapper

from Pub.ORM import Url, sessionmaker, engine


class clientWork:
    queueStartName = "clientReceive"
    queueEndName = "clientEnd"
    queueResultName = "clientResult"
    url = ""
    level = ""
    rabbitMqServerIP = ""
    rabbitMqServerPort = ""
    username = ""
    password = ""
    num=10
    def sendTask(self,url,num=10,level="1"):
        session=self.Session()
        u=session.query(Url).filter_by(url=url).first()
        url_id=0
        if(u is None):
            u=Url(url=url)
            session.add(u)
            session.commit()
        url_id=u.url_id

        for i in range(num):
            infor = {"url":url,"url_id":url_id, "level": self.level, "request_id":random.randint(0,100000000)}
            body = json.dumps(infor)
            self.sendChannel.basic_publish(exchange = '', routing_key = self.queueStartName, body = body)


    def __init__(self):
        self.Session=sessionmaker(engine)
        self.rabbitMQ=RabbitMQWrapper()
        self.sendChannel = self.rabbitMQ.getChannel()
        self.sendChannel.queue_declare(queue = self.queueStartName)
