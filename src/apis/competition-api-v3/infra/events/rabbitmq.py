import json

import pika
from django.conf import settings
from pika.exceptions import AMQPError


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASSWORD,
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=60,
                blocked_connection_timeout=300,
            )
        )
        self.channel = self.connection.channel()

    def publish(self, routing_key, body):
        try:
            if (
                self.connection is None
                or self.connection.is_closed
                or self.channel.is_closed
            ):
                self.connect()

            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(body),
            )
        except AMQPError:
            self.connect()
            self.channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(body),
            )
