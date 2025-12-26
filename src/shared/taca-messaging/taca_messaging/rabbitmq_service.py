import inspect
import json
import logging
import os
import re
from typing import Callable, Dict, Optional

import aio_pika
from aio_pika import ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection


class RabbitMQService:
    """
    RabbitMQ service for managing connections, publishing, and consuming events.

    Architecture:
    - Uses topic exchange for pub/sub pattern
    - Each service has its own queue (named by service_name)
    - Multiple instances of the same service share the same queue (load balancing)
    - Different services get the same event (no load balancing across services)

    Usage:
        rabbitmq = RabbitMQService(service_name="matches-service")

        @rabbitmq.event_handler('match.created')
        async def handle_match_created(data: dict):
            print(f"Match created: {data}")

        await rabbitmq.publish_event('match.created', {'id': 123})
    """

    def __init__(
        self,
        service_name: str,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        exchange_name: str = "events",
        logger: Optional[logging.Logger] = None,
    ):
        if not service_name:
            raise ValueError("service_name is required")

        self.service_name = service_name
        self.host = host or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port or int(os.getenv("RABBITMQ_PORT", "5672"))
        self.user = user or os.getenv("RABBITMQ_USER", "guest")
        self.password = password or os.getenv("RABBITMQ_PASSWORD", "guest")
        self.exchange_name = exchange_name
        self.logger = logger or logging.getLogger(__name__)

        self.connection: AbstractRobustConnection | None = None
        self.channel = None
        self.exchange = None

        # Store event handlers: {event_name: [handler_func1, handler_func2, ...]}
        self.event_handlers: Dict[str, list[Callable]] = {}

    async def connect(self):
        """Establish connection to RabbitMQ."""
        if self.connection is None or self.connection.is_closed:
            self.connection = await connect_robust(
                host=self.host,
                port=self.port,
                login=self.user,
                password=self.password,
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            # Declare exchange for pub/sub pattern
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,
            )
        return self.connection

    async def disconnect(self):
        """Close the RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.exchange = None

    def event_handler(self, event_name: str):
        """
        Decorator to register an event handler function.

        Usage:
            @rabbitmq_service.event_handler('match.created')
            async def process_match_created(data: dict):
                print(f"Match created: {data}")

        Args:
            event_name: The event name/routing key to listen for (supports wildcards like 'match.*')
        """

        def decorator(func: Callable):
            # Register the handler
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            return func

        return decorator

    async def _process_message(
        self,
        message: AbstractIncomingMessage,
        handler: Callable,
    ):
        """Internal method to process incoming messages."""
        body = message.body.decode("utf-8")
        data = json.loads(body)

        # Check if handler is async or sync
        if inspect.iscoroutinefunction(handler):
            await handler(data)
        else:
            handler(data)

        self.logger.info(
            f"Processed event '{message.routing_key}' with handler '{handler.__name__}'"
        )

    async def start_consuming(self):
        """
        Start consuming events for all registered event handlers.

        Uses service_name as the queue name, ensuring:
        - Multiple instances of the same service share the queue (load balancing)
        - Different services have different queues (both receive events)
        """
        await self.connect()

        if not self.event_handlers:
            self.logger.warning(
                "No event handlers registered. Use @event_handler decorator to register handlers."
            )
            return

        # Queue name based on service name (same for all instances of this service)
        queue_name = f"{self.service_name}.events"

        # Declare queue (shared by all instances of this service)
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            auto_delete=False,
        )

        # Bind queue to exchange for each registered event pattern
        for event_pattern in self.event_handlers.keys():
            await queue.bind(self.exchange, routing_key=event_pattern)
            self.logger.info(
                f"Bound queue '{queue_name}' to event pattern '{event_pattern}'"
            )

        # Start consuming using the extracted handler to reduce complexity
        await queue.consume(self._on_message)
        self.logger.info(f"Started consuming events from queue: {queue_name}")

    async def _on_message(self, message: AbstractIncomingMessage):
        routing_key = message.routing_key
        processed = False

        # Find all matching handlers
        try:
            for event_pattern, handlers in self.event_handlers.items():
                if self._matches_pattern(routing_key, event_pattern):
                    for handler in handlers:
                        await self._process_message(message, handler)
                        processed = True

            # Acknowledge message once after all handlers have processed it
            if processed:
                await message.ack()
            else:
                self.logger.warning(f"No handlers matched routing key: {routing_key}")
                await message.ack()  # Ack anyway to prevent requeue
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode message: {e}")
            await message.reject(requeue=False)  # Reject malformed messages
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            await message.reject(requeue=True)  # Requeue for retry

    def _matches_pattern(self, routing_key: str, pattern: str) -> bool:
        """
        Check if routing key matches the event pattern.
        Supports RabbitMQ topic patterns: * (one word), # (zero or more words)
        """
        if pattern == routing_key:
            return True

        regex_pattern = (
            pattern.replace("#.", "#")
            .replace(".#", "#")
            .replace(".", r"\.")
            .replace("*", r"[^\.]+")
            .replace("#", r"(.+)?")
        )

        print(regex_pattern)

        return re.fullmatch(regex_pattern, routing_key) is not None

    async def publish_event(self, event_name: str, data: dict):
        """
        Publish an event to the exchange.
        All services listening to this event pattern will receive it.

        Args:
            event_name: The event name/routing key (e.g., 'match.created')
            data: Dictionary containing event data
        """
        await self.connect()

        message = Message(
            body=json.dumps(data).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        await self.exchange.publish(
            message,
            routing_key=event_name,
        )
        self.logger.info(f"Published event '{event_name}'")
