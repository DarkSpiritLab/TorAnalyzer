import json
import pika

with open("receiveConfig.json") as f:
    config = json.loads(f.read())

class RabbitMQWarpper:
    def __init__(self):
        pass

    def getConfig(self):
        return config

    def getChannel(self):
        credentials = pika.PlainCredentials(config.pikaAccount, config.pikaPassword)
        connectionRabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(config.rabbitMqServerIP, config.rabbitMqServerPort, '/', credentials))
        channel = connectionRabbitMQ.channel()
        return channel
