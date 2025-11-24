import json
import os

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


async def consume():
    consumer = AIOKafkaConsumer(
        "ranking-topic",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="ranking-service-group",
    )
    try:
        await consumer.start()
        try:
            async for msg in consumer:
                print(f"Consumed: {msg.value}")
        finally:
            await consumer.stop()
    except Exception as e:
        print(f"Kafka consumer error: {e}")


async def produce(topic, message):
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        await producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))
    finally:
        await producer.stop()
