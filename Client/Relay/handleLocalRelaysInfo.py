# curl --socks5-hostname 127.0.0.1:9011 6gi7ufqbqnllbbvx.onion
import base64
import json
import os
import signal
import socket
import sys
from os import path

s = path.abspath(__file__)
with open(path.split(s)[0] + "/relayConfig.json") as f:
    s1 = f.read()
    j = json.loads(s1)

for i in range(3):
    s = path.split(s)[0]
sys.path.append(s)

from threading import Thread

from Pub.myutil import *

from Pub.RabbitMQ import RabbitMQWrapper, RabbitMQInfo


def exiter(_1, _2):
    os._exit(0)


class LocalRelayInfoHandler:
    def __init__(self):
        self.localIP = get_host_ip()
        self.rabbitMQ = RabbitMQWrapper()
        self.connInfo = RabbitMQInfo.connInfo
        self.cellInfo = RabbitMQInfo.cellInfo
        self.connChannel = self.rabbitMQ.getChannel()
        self.cellChannel = self.rabbitMQ.getChannel()

        self.connChannel.queue_declare(queue = self.connInfo)

        self.cellChannel.queue_declare(queue = self.cellInfo)

        self.conninfo_address = j["connInfoAddress"]
        self.cell_address = j["cellAddress"]
        # if (not os.path.exists(path)):
        #     try:
        #         os.mkdir(path)
        #     except:
        #         print("failed to mkdir")
        # Make sure the socket does not already exist
        try:
            os.unlink(self.conninfo_address)
            os.unlink(self.cell_address)
        except OSError:
            if os.path.exists(self.conninfo_address):
                raise "file exists"

    def handleConnBody(self, body):
        '''
    {
      "type":"%s",
      "info":{
        "next_ip":"%u.%u.%u.%u",
        "last_port":%u,
        "prev_circ_id":%u,
        "next_circ_id":%u,
        "stream_id":%u,
        "direction":%d
        }
    }
        :param body:
        :return:
        '''
        # add my_ip into info
        if (body is not None and len(body) > 0):
            s = body.decode("utf-8")
            if (s is None):
                return
            d = json.loads(s)
            if ("info" in d):
                d["info"]["my_ip"] = self.localIP
                s = json.dumps(d)
                if (s is None):
                    return
                if(self.connChannel.is_closed):
                    self.connChannel=self.rabbitMQ.getChannel()
                    self.connChannel.queue_declare(queue=self.connChannel)
                self.connChannel.basic_publish(exchange = "", routing_key = self.connInfo, body = s)


    def handleCellBody(self, body):
        # trans to json format
        d = {"cell": base64.b64encode(body).decode("utf-8"), "my_ip": self.localIP}
        s = json.dumps(d)
        if (s is not None):
            # print(s)
            if(self.cellChannel.is_closed):
                self.cellChannel=self.rabbitMQ.getChannel()
                self.cellChannel.queue_declare(queue = self.cellInfo)
            self.cellChannel.basic_publish(exchange = "", routing_key = self.cellInfo, body = s)


    def listenSocketFile(self, kind, targetMethod):
        # Create a UDS socket
        if (kind == 1):
            address = self.conninfo_address
        else:
            address = self.cell_address
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # Set REUSEADDR and bind the socket to the port
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 10)
        # print(address)
        try:
            os.remove(address)
        except:
            pass
        finally:
            sock.bind(address)

        # Listen for incoming connections
        sock.listen(100)
        try:
            while True:
                # Wait for a connection
                try:
                    connection, client_address = sock.accept()
                    data = bytes()
                    # Receive the data in small chunks and retransmit it
                    while True:
                        temp = connection.recv(10000)
                        if len(temp) == 0:
                            break
                        data += temp
                    if (data is not None and len(data) > 0):
                        targetMethod(self, data)
                finally:
                    # Clean up the connection
                    connection.close()
        finally:
            sock.close()

    def startHandleLocalRelaysInfo(self):
        signal.signal(signal.SIGINT, exiter)
        cellThread = Thread(target = LocalRelayInfoHandler.listenSocketFile,
            args = (self, 0, LocalRelayInfoHandler.handleCellBody))
        cellThread.start()
        connThread = Thread(target = LocalRelayInfoHandler.listenSocketFile,
            args = (self, 1, LocalRelayInfoHandler.handleConnBody))
        connThread.start()


if __name__ == "__main__":
    # test
    print("handleLocalRelaysInfo start")
    LocalRelayInfoHandler().startHandleLocalRelaysInfo()
