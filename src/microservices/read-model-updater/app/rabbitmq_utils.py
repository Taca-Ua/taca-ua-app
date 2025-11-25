import json
import os
from typing import Callable

import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractRobustConnection

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

connection: AbstractRobustConnection | None = None


async def get_connection():
    global connection
    if connection is None or connection.is_closed:
        connection = await connect_robust(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USER,
            password=RABBITMQ_PASSWORD,
        )
    return connection


async def consume(
    queue_name: str = "read-model-queue", callback: Callable | None = None
):
    """
    Consume messages from a RabbitMQ queue.

    Args:
        queue_name: Name of the queue to consume from
        callback: Optional callback function to process messages.
                  If None, messages are just printed.
    """
    conn = await get_connection()
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(queue_name, durable=True)

    async def on_message(message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                body = message.body.decode("utf-8")
                data = json.loads(body)
                print(f"Consumed: {data}")

                if callback:
                    await callback(data)
            except Exception as e:
                print(f"RabbitMQ consumer error: {e}")

    await queue.consume(on_message)
    print(f"Started consuming from queue: {queue_name}")


async def produce(queue_name: str, message: dict):
    """
    Produce a message to a RabbitMQ queue.

    Args:
        queue_name: Name of the queue to send to
        message: Dictionary to send as JSON
    """
    conn = await get_connection()
    channel = await conn.channel()

    queue = await channel.declare_queue(queue_name, durable=True)

    await channel.default_exchange.publish(
        Message(
            body=json.dumps(message).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=queue.name,
    )


async def close_connection():
    """Close the RabbitMQ connection."""
    global connection
    if connection and not connection.is_closed:
        await connection.close()
