# coding=utf-8
'''
Receive message from queue,paser it,and insert it into MySQL or sqlite
'''
import time
from threading import Thread

from Pub.RabbitMQ import RabbitMQWrapper
from Pub.ORM import *


class RealysMessageHandler:
    def __init__(self):
        rabbitMQ=RabbitMQWrapper()
        config = rabbitMQ.getConfig()
        self.connInfo = config["connInfo"]
        self.cellInfo = config["cellInfo"]
        self.connChannel = rabbitMQ.getChannel()
        self.connChannel.queue_declare(queue = self.connInfo)
        self.cellChannel = rabbitMQ.getChannel()
        self.cellChannel.queue_declare(queue = self.cellInfo)
        self.Session = sessionmaker(bind = engine)

    def startReceive(self):
        '''
        :return:
        '''
        # using two threads to handle both connInfo and cellInfo
        connThread = Thread(target = self.handleConnInfo)
        # cellThread = Thread(target = RealysMessageHandler.handleCellInfo, args = (self))
        connThread.start()
        # cellThread.start()
        connThread.join()
        # cellThread.join()
        print("thread stopped")

    def handleConnInfo(self):
        for method_fram, properties, body in self.connChannel.consume(self.connInfo):
            self.connChannel.basic_ack(delivery_tag = method_fram.delivery_tag)
            # handle the body

            d = json.loads(body.encode("utf8"))
            if ("type" not in d or "info" not in d):
                return
            if (d["type"] == "pack"):  # client
                try:
                    with open("./currentTask", "r+") as f:
                        s = f.readlines()
                        if (len(s) == 2):
                            # first is request_id and second is url_id
                            request_id = int(s[0], 10)
                            url_id = int(s[1], 10)
                except:
                    print("error in pasering currentTask file")
                l = d["info"]
                link = Link(request_id = request_id, url_id = url_id, datetime = time.time()
                    , prev_circ_id = l["last_circ_id"], next_circ_id = l["next_circ_id"], my_ip = l["my_ip"]
                    , next_ip = l["next_ip"], next_port = l["port"], direction = l["direction"]
                    , stream_id = l["stream_id"], is_origin = 1)
            else:  # others such as "relay" and "join"
                l = d["info"]
                link = Link(datetime = time.time()
                    , prev_circ_id = l["last_circ_id"], next_circ_id = l["next_circ_id"], my_ip = l["my_ip"]
                    , next_ip = l["next_ip"], next_port = l["port"], direction = l["direction"]
                    , stream_id = l["stream_id"], is_origin = 0)
            session = self.Session()
            session.add(link)
            session.commit()
            # todo add handle cell info
            #   remove this to other's
            # def handleCellInfo(self):
            #     for method_fram, properties, body in self.channel.consume(self.cellInfo):
            #         self.cellChannel.basic_ack(delivery_tag = method_fram.delivery_tag)
            #         # handle the body

if __name__ =="__main__":
    RealysMessageHandler().startReceive()