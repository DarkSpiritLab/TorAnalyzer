import json
import pika
from os import path

with open(path.join(path.split(__file__)[0],"receiveConfig.json"))as f:
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
            print("Failed to connect to RabbitMQ")
            exit(0)
    def __del__(self):
        try:
            self.connectionRabbitMQ.close()
        except:
            pass

    def getConfig(self):
        return config

    def getChannel(self):
        self.connectionRabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(RabbitMQInfo.rabbitMqServerIP, RabbitMQInfo.rabbitMqServerPort, '/',
                self.credentials))
        channel = self.connectionRabbitMQ.channel()
        return channel
    def closeConnection(self):
        try:
            self.connectionRabbitMQ.close()
        except:
            print("Failed to close RabbitMQ connection")
