# curl --socks5-hostname 127.0.0.1:9011 6gi7ufqbqnllbbvx.onion

import socket
import sys
import os
import base64
import signal
from threading import Thread

import pika
import json
from myutil import *

localIP = get_host_ip()

with open("receiveConfig.json") as f:
    config = json.loads(f.read())
    rabbitMqServerIP = config["rabbitMqServerIP"]
    rabbitMqServerPort = config["rabbitMqServerPort"]
credentials = pika.PlainCredentials("test", "test")
connectionRabbitMQ = pika.BlockingConnection(
    pika.ConnectionParameters(rabbitMqServerIP, rabbitMqServerPort, '/', credentials))
connInfo = config["connInfo"]
cellInfo = config["cellInfo"]
connChannel = connectionRabbitMQ.channel()
connChannel.queue_declare(queue = connInfo)
cellChannel = connectionRabbitMQ.channel()
cellChannel.queue_declare(queue = cellInfo)

path = "/tor_release"
conninfo_address = path + '/conninfo'
cell_address = path + '/cell'
if (not os.path.exists(path)):
    try:
        os.mkdir(path)
    except:
        print("failed to mkdir")
# Make sure the socket does not already exist
try:
    os.unlink(conninfo_address)
except OSError:
    if os.path.exists(conninfo_address):
        raise "file exists"


def exiter(_1, _2):
    try:
        pass
        # connectionRabbitMQ.close()
    except:
        pass
    os._exit(0)


def handleConnBody(body):
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
    #add my_ip into info
    if (body is not None and len(body) > 0):
        s = body.decode("utf-8")
        if (s is not None):
            d = json.loads(s)
            if ("info" in d):
                d["info"]["my_ip"] = localIP
                s = json.dumps(d)
                connChannel.basic_publish(exchange = "", routing_key = connInfo, body = s)


def handleCellBody(body):
    # trans to json format
    d = {"cell": base64.b64encode(body).decode("utf-8"), "my_ip": localIP}
    s = json.dumps(d)
    if (s != None):
        print(s)
        cellChannel.basic_publish(exchange = "", routing_key = cellInfo, body = s)


def listenSocketFile(kind, targetMethod):
    # Create a UDS socket
    if (kind == 1):
        address = conninfo_address
    else:
        address = cell_address
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Set REUSEADDR and bind the socket to the port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 10)
    print(address)
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
                    targetMethod(data)
            finally:
                # Clean up the connection
                connection.close()
    finally:
        sock.close()


if __name__ == "__main__":
    # test
    signal.signal(signal.SIGINT, exiter)
    cellThread = Thread(target = listenSocketFile, args = (0, handleCellBody))
    cellThread.start()
    connThread = Thread(target = listenSocketFile, args = (1, handleConnBody))
    connThread.start()
    cellThread.join()
    connThread.join()
    try:
        connectionRabbitMQ.close()
    except:
        pass
