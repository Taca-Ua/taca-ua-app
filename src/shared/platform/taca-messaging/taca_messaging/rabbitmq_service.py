import inspect
import json
import logging
import os
import re
from typing import Callable, Dict, Optional, Type, Union

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

        # Metrics
        self.processed_messages = 0
        self.failed_processed_messages = 0

        # Store event handlers: {event_name: [{"handler": func, "schema": cls or None}, ...]}
        self.event_handlers: Dict[str, list[dict]] = {}

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

    def event_handler(self, event_source: Union[str, Type]):
        """
        Decorator to register an event handler function.

        Accepts either a routing key string (legacy) or an EventSchema subclass (typed).

        String usage (legacy):
            @rabbitmq_service.event_handler('match.created')
            async def process_match_created(data: dict):
                ...

        Typed usage (new):
            @rabbitmq_service.event_handler(MatchCreatedV1)
            async def process_match_created(event: MatchCreatedV1):
                ...

        Args:
            event_source: Routing key string OR EventSchema subclass with a
                          ``routing_key()`` classmethod.
        """
        if isinstance(event_source, str):
            event_name = event_source
            schema_class = None
        elif isinstance(event_source, type) and hasattr(event_source, "routing_key"):
            event_name = event_source.routing_key()
            schema_class = event_source
        else:
            raise TypeError(
                f"event_handler expects a str or EventSchema subclass, "
                f"got {type(event_source)}"
            )

        def decorator(func: Callable):
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(
                {"handler": func, "schema": schema_class}
            )
            return func

        return decorator

    async def _process_message(
        self,
        message: AbstractIncomingMessage,
        entry: dict,
    ):
        """Internal method to process incoming messages."""
        body = message.body.decode("utf-8")
        data = json.loads(body)
        inner_data = data.get("data", None)

        handler = entry["handler"]
        schema_class = entry["schema"]

        if schema_class is not None:
            # Typed handler: automatically parse the event via EventRegistry
            try:
                from taca_events.pydantic_schemas.registry import EventRegistry

                routing_key = schema_class.routing_key()
                typed_event = EventRegistry.parse(routing_key, inner_data or {})
            except KeyError as e:
                self.logger.error(
                    f"No schema registered for '{schema_class.__name__}': {e}"
                )
                return
            except Exception as e:
                self.logger.error(
                    f"Failed to parse event for '{schema_class.__name__}': {e}"
                )
                return

            if inspect.iscoroutinefunction(handler):
                await handler(typed_event)
            else:
                handler(typed_event)
        else:
            # Legacy handler: pass the raw inner data dict
            if inspect.iscoroutinefunction(handler):
                await handler(inner_data)
            else:
                handler(inner_data)

        self.processed_messages += 1
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

        print(f"Received message with routing key: {routing_key}")

        # Find all matching handlers
        try:
            for event_pattern, entries in self.event_handlers.items():
                if self._matches_pattern(routing_key, event_pattern):
                    for entry in entries:
                        await self._process_message(message, entry)
                        processed = True

            # Acknowledge message once after all handlers have processed it
            if processed:
                await message.ack()
            else:
                self.logger.warning(f"No handlers matched routing key: {routing_key}")
                await message.ack()  # Ack anyway to prevent requeue
        except json.JSONDecodeError as e:
            self.failed_processed_messages += 1
            self.logger.error(f"Failed to decode message: {e}")
            await message.reject(requeue=False)  # Reject malformed messages
        except Exception as e:
            self.failed_processed_messages += 1
            self.logger.error(f"Error processing message: {e}")
            await message.reject(requeue=False)  # Requeue for retry

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
