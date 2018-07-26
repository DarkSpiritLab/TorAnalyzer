import json
import pika
from os import path

with open(path.join(path.split(__file__)[0], "receiveConfig.json"))as f:
    config = json.loads(f.read())


class RabbitMQInfo:
    rabbitMqServerIP = config["rabbitMqServerIP"]
    rabbitMqServerPort = config["rabbitMqServerPort"]
    username = config["pikaAccount"]
    password = config["pikaPassword"]
    sqlFilePath = config["sqlFilePath"]
    pikaAccount = config["pikaAccount"]
    pikaPassword = config["pikaPassword"]
    reverseResultQueue = config["reverseResultQueue"]
    connInfo = config["connInfo"]
    cellInfo = config["cellInfo"]


class RabbitMQWrapper:
    def __init__(self):
        print("RabbitMQWrapper init")
        try:
            self.credentials = pika.PlainCredentials(RabbitMQInfo.pikaAccount, RabbitMQInfo.pikaPassword)
        except:
            print("Failed to connect RabbitMQ")
            exit()
        self.connections={}
    def getConfig(self):
        return config

    def getChannel(self):
        connection = RabbitMQConnection(credentials = self.credentials)
        channel=connection.getChannel()
        self.connections[channel]=connection
        return channel

    def closeChannel(self, channel):
        try:
            self.connections[channel].close()
        except:
            print("Failed to close RabbitMQ connection")


class RabbitMQConnection():
    def __init__(self, credentials):
        times = 5
        while (times > 0):
            try:
                self.connectionRabbitMQ = pika.BlockingConnection(
                    pika.ConnectionParameters(RabbitMQInfo.rabbitMqServerIP, RabbitMQInfo.rabbitMqServerPort, '/',
                        credentials))
            except:
                print("Failed to connect RabbitMQ")
                times -= 1
                continue
            break
        if (times == 0):
            exit(0)

    def getChannel(self):
        return self.connectionRabbitMQ.channel()
