"""
Example usage of the RabbitMQ service with event handlers.

Key concepts:
1. Each service creates its own RabbitMQService instance with a unique service_name
2. Multiple instances of the same service (same service_name) will load-balance events
3. Different services (different service_names) will all receive the same events
"""

import asyncio

from taca_messaging.rabbitmq_service import RabbitMQService

# Create RabbitMQ instance for this service
# All instances of "matches-service" will share the same queue
rabbitmq = RabbitMQService(service_name="matches-service")


# Register event handlers using the decorator
@rabbitmq.event_handler("match.created")
async def handle_match_created(data: dict):
    """Handle match.created events."""
    print(f"[matches-service] Processing match created: {data}")
    match_id = data.get("match_id")
    print(f"[matches-service] New match ID: {match_id}")


@rabbitmq.event_handler("match.updated")
async def handle_match_updated(data: dict):
    """Handle match.updated events."""
    print(f"[matches-service] Processing match updated: {data}")


# Wildcard pattern - handles all match events
@rabbitmq.event_handler("match.*")
async def log_all_match_events(data: dict):
    """Log all match-related events."""
    print(f"[AUDIT] Match event: {data}")


# You can also have synchronous handlers
@rabbitmq.event_handler("notification.send")
def send_notification(data: dict):
    """Send a notification (synchronous example)."""
    print(f"Sending notification: {data.get('message')}")


async def consumer_main():
    """
    Main function to start the event consumer.
    Call this in your FastAPI lifespan or startup event.
    """
    # Start consuming events
    await rabbitmq.start_consuming()

    # Keep the consumer running
    print("Event consumer is running. Press Ctrl+C to exit.")
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\nShutting down...")
        await rabbitmq.disconnect()


async def publisher_example():
    """Example of how to publish events from any service."""
    # You can publish from any service (doesn't have to be matches-service)
    publisher = RabbitMQService(service_name="api-service")

    # Publish events
    await publisher.publish_event(
        "match.created",
        {
            "match_id": 123,
            "team1": "Team A",
            "team2": "Team B",
            "scheduled_time": "2025-11-25T18:00:00Z",
        },
    )

    await publisher.publish_event(
        "match.updated",
        {"match_id": 123, "status": "in_progress", "score": {"team1": 1, "team2": 0}},
    )

    await publisher.disconnect()


# Example: Multiple services listening to the same event
async def simulate_multiple_services():
    """
    Demonstrates how different services all receive the same event,
    but multiple instances of the same service load-balance.
    """
    # Service 1: Matches Service
    matches_service = RabbitMQService(service_name="matches-service")

    @matches_service.event_handler("match.created")
    async def matches_handler(data: dict):
        print(f"[matches-service] Received: {data}")

    # Service 2: Ranking Service (different service, will also receive events)
    ranking_service = RabbitMQService(service_name="ranking-service")

    @ranking_service.event_handler("match.created")
    async def ranking_handler(data: dict):
        print(f"[ranking-service] Received: {data}")

    # Start both consumers
    await matches_service.start_consuming()
    await ranking_service.start_consuming()

    # Publish an event
    publisher = RabbitMQService(service_name="publisher")
    await publisher.publish_event("match.created", {"match_id": 999})

    # Both services will receive the event!
    await asyncio.sleep(2)

    # Cleanup
    await matches_service.disconnect()
    await ranking_service.disconnect()
    await publisher.disconnect()


if __name__ == "__main__":
    # Run the consumer
    # asyncio.run(consumer_main())

    # Or test publishing:
    # asyncio.run(publisher_example())

    # Or simulate multiple services:
    asyncio.run(simulate_multiple_services())
