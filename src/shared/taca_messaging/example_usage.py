"""
Example usage of the RabbitMQ service with event handlers.
This demonstrates how to use the @event_handler decorator.
"""

import asyncio
import sys
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
from messaging import event_handler, rabbitmq_service


# Method 1: Using the global event_handler decorator
@event_handler("match.created")
async def process_match_created(data: dict):
    """Handle match.created events."""
    print(f"Processing match created event: {data}")
    # Your business logic here
    match_id = data.get("match_id")
    print(f"New match created with ID: {match_id}")


@event_handler("match.updated")
async def process_match_updated(data: dict):
    """Handle match.updated events."""
    print(f"Processing match updated event: {data}")
    match_id = data.get("match_id")
    print(f"Match {match_id} was updated")


@event_handler("match.deleted")
async def process_match_deleted(data: dict):
    """Handle match.deleted events."""
    print(f"Processing match deleted event: {data}")
    match_id = data.get("match_id")
    print(f"Match {match_id} was deleted")


# Wildcard pattern - handles all match events
@event_handler("match.*")
async def log_all_match_events(data: dict):
    """Log all match-related events."""
    print(f"[AUDIT] Match event occurred: {data}")


# You can also have synchronous handlers
@event_handler("user.notification")
def send_notification(data: dict):
    """Send a notification (synchronous example)."""
    print(f"Sending notification: {data.get('message')}")


async def main():
    """
    Main function to start the event consumer.
    This would typically be called in your FastAPI startup event.
    """
    # Start consuming events
    await rabbitmq_service.start_consuming(queue_name="matches-service-queue")

    # Keep the consumer running
    print("Event consumer is running. Press Ctrl+C to exit.")
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\nShutting down...")
        await rabbitmq_service.disconnect()


async def example_publish():
    """Example of how to publish events."""
    # Publish a match.created event
    await rabbitmq_service.publish_event(
        "match.created",
        {
            "match_id": 123,
            "team1": "Team A",
            "team2": "Team B",
            "scheduled_time": "2025-11-25T18:00:00Z",
        },
    )

    # Publish a match.updated event
    await rabbitmq_service.publish_event(
        "match.updated",
        {"match_id": 123, "status": "in_progress", "score": {"team1": 1, "team2": 0}},
    )


if __name__ == "__main__":
    # Run the consumer
    # asyncio.run(main())

    # Or if you want to test publishing:
    asyncio.run(example_publish())
