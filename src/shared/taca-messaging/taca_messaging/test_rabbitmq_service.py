import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from .rabbitmq_service import RabbitMQService


class TestRabbitMQServiceInitialization:
    """Test suite for RabbitMQService initialization."""

    def test_service_name_required(self):
        """Test that service_name is required."""
        with pytest.raises(ValueError, match="service_name is required"):
            RabbitMQService(service_name="")

        with pytest.raises(ValueError, match="service_name is required"):
            RabbitMQService(service_name=None)

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        service = RabbitMQService(service_name="test-service")

        assert service.service_name == "test-service"
        assert service.host == "localhost"
        assert service.port == 5672
        assert service.user == "guest"  # pragma: allowlist secret
        assert service.password == "guest"  # pragma: allowlist secret
        assert service.exchange_name == "events"
        assert service.connection is None
        assert service.channel is None
        assert service.exchange is None
        assert service.event_handlers == {}

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        service = RabbitMQService(
            service_name="custom-service",
            host="rabbitmq.example.com",
            port=5673,
            user="admin",  # pragma: allowlist secret
            password="secret",  # pragma: allowlist secret
            exchange_name="custom_exchange",
        )

        assert service.service_name == "custom-service"
        assert service.host == "rabbitmq.example.com"
        assert service.port == 5673
        assert service.user == "admin"
        assert service.password == "secret"  # pragma: allowlist secret
        assert service.exchange_name == "custom_exchange"

    @patch.dict("os.environ", {"RABBITMQ_HOST": "env-host", "RABBITMQ_PORT": "5674"})
    def test_initialization_with_env_vars(self):
        """Test initialization using environment variables."""
        service = RabbitMQService(service_name="test-service")

        assert service.host == "env-host"
        assert service.port == 5674


class TestPatternMatching:
    """Test suite for routing key pattern matching logic."""

    @pytest.fixture
    def service(self):
        """Create a RabbitMQService instance for testing."""
        return RabbitMQService(service_name="test-service")

    def test_exact_match(self, service):
        """Test exact routing key match."""
        assert service._matches_pattern("match.created", "match.created") is True
        assert service._matches_pattern("match.updated", "match.created") is False

    def test_single_wildcard_match(self, service):
        """Test single wildcard (*) pattern matching."""
        # Single wildcard matches exactly one word
        assert service._matches_pattern("match.created", "match.*") is True
        assert service._matches_pattern("match.updated", "match.*") is True
        assert service._matches_pattern("tournament.started", "match.*") is False
        assert service._matches_pattern("match.created.v2", "match.*") is False

        # Multiple wildcards
        assert service._matches_pattern("match.created.v1", "match.*.v1") is True
        assert service._matches_pattern("match.updated.v2", "match.*.v1") is False
        assert service._matches_pattern("match.created", "*.created") is True

    def test_hash_wildcard_match(self, service):
        """Test hash wildcard (#) pattern matching."""
        # Hash matches zero or more words
        assert service._matches_pattern("match.created", "match.#") is True
        assert service._matches_pattern("match.created.v1", "match.#") is True
        assert service._matches_pattern("match.created.v1.final", "match.#") is True
        assert service._matches_pattern("match", "match.#") is True
        assert service._matches_pattern("tournament.created", "match.#") is False

        # Hash at the beginning
        assert service._matches_pattern("event.match.created", "#.created") is True
        assert service._matches_pattern("created", "#.created") is True

        # Hash in the middle
        assert service._matches_pattern("match.created.v1", "match.#.v1") is True
        assert service._matches_pattern("match.v1", "match.#.v1") is True
        assert (
            service._matches_pattern("match.created.updated.v1", "match.#.v1") is True
        )
        assert service._matches_pattern("match.v1.extra", "match.#.v1") is False
        assert service._matches_pattern("match.created", "match.#.v1") is False

    def test_combined_wildcards(self, service):
        """Test combinations of wildcards."""
        assert service._matches_pattern("match.created.v1", "*.created.*") is True
        assert service._matches_pattern("match.updated.v2", "*.updated.*") is True
        assert service._matches_pattern("match.created", "*.created.*") is False

    def test_no_match(self, service):
        """Test cases where patterns don't match."""
        assert service._matches_pattern("match.created", "tournament.created") is False
        assert service._matches_pattern("match", "match.created") is False
        assert service._matches_pattern("match.created.v1", "match.created") is False


class TestEventHandlerRegistration:
    """Test suite for event handler registration."""

    @pytest.fixture
    def service(self):
        """Create a RabbitMQService instance for testing."""
        return RabbitMQService(service_name="test-service")

    def test_register_single_handler(self, service):
        """Test registering a single event handler."""

        @service.event_handler("match.created")
        async def handler1(data: dict):
            """Temporary test handler."""
            pass

        assert "match.created" in service.event_handlers
        assert len(service.event_handlers["match.created"]) == 1
        assert service.event_handlers["match.created"][0] == handler1

    def test_register_multiple_handlers_different_events(self, service):
        """Test registering handlers for different events."""

        @service.event_handler("match.created")
        async def handler1(data: dict):
            """Temporary test handler."""
            pass

        @service.event_handler("match.updated")
        async def handler2(data: dict):
            """Temporary test handler."""
            pass

        assert "match.created" in service.event_handlers
        assert "match.updated" in service.event_handlers
        assert len(service.event_handlers["match.created"]) == 1
        assert len(service.event_handlers["match.updated"]) == 1

    def test_register_multiple_handlers_same_event(self, service):
        """Test registering multiple handlers for the same event."""

        @service.event_handler("match.created")
        async def handler1(data: dict):
            """Temporary test handler."""
            pass

        @service.event_handler("match.created")
        async def handler2(data: dict):
            """Temporary test handler."""
            pass

        assert "match.created" in service.event_handlers
        assert len(service.event_handlers["match.created"]) == 2
        assert handler1 in service.event_handlers["match.created"]
        assert handler2 in service.event_handlers["match.created"]

    def test_handler_with_wildcard_pattern(self, service):
        """Test registering handlers with wildcard patterns."""

        @service.event_handler("match.*")
        async def handler1(data: dict):
            """Temporary test handler."""
            pass

        @service.event_handler("*.created")
        async def handler2(data: dict):
            """Temporary test handler."""
            pass

        assert "match.*" in service.event_handlers
        assert "*.created" in service.event_handlers


class TestMessageProcessing:
    """Test suite for message processing logic."""

    @pytest.fixture
    def service(self):
        """Create a RabbitMQService instance for testing."""
        return RabbitMQService(service_name="test-service")

    @pytest.mark.asyncio
    async def test_process_message_with_async_handler(self, service):
        """Test processing message with async handler."""
        handler_called = False
        received_data = None

        async def async_handler(data: dict):  # NOSONAR
            nonlocal handler_called, received_data
            handler_called = True
            received_data = data

        message = Mock()
        message.body = json.dumps({"id": 123, "name": "test"}).encode("utf-8")
        message.routing_key = "test.event"

        await service._process_message(message, async_handler)

        assert handler_called is True
        assert received_data == {"id": 123, "name": "test"}  # NOSONAR

    @pytest.mark.asyncio
    async def test_process_message_with_sync_handler(self, service):
        """Test processing message with sync handler."""
        handler_called = False
        received_data = None

        def sync_handler(data: dict):
            nonlocal handler_called, received_data
            handler_called = True
            received_data = data

        message = Mock()
        message.body = json.dumps({"id": 456, "status": "active"}).encode("utf-8")
        message.routing_key = "test.event"

        await service._process_message(message, sync_handler)

        assert handler_called is True
        assert received_data == {"id": 456, "status": "active"}  # NOSONAR

    @pytest.mark.asyncio
    async def test_process_message_with_multiple_handlers(self, service):
        """Test that multiple handlers can be registered and called for the same event."""
        handler1_called = False
        handler2_called = False

        @service.event_handler("match.created")
        async def handler1(data: dict):
            nonlocal handler1_called
            handler1_called = True

        @service.event_handler("match.created")
        async def handler2(data: dict):
            nonlocal handler2_called
            handler2_called = True

        # Simulate processing a message
        message = Mock()
        message.body = json.dumps({"id": 789}).encode("utf-8")
        message.routing_key = "match.created"

        # Process with both handlers
        await service._process_message(message, handler1)
        await service._process_message(message, handler2)

        assert handler1_called is True
        assert handler2_called is True


class TestMessageRoutingIntegration:
    """Integration tests for complete message routing flow."""

    @pytest.fixture
    def service(self):
        """Create a RabbitMQService instance for testing."""
        return RabbitMQService(service_name="test-service")

    @pytest.mark.asyncio
    async def test_routing_to_wildcard_handlers(self, service):
        """Test that messages are routed to handlers with wildcard patterns."""
        handler1_data = None
        handler2_data = None
        handler3_data = None

        @service.event_handler("match.created")
        async def exact_handler(data: dict):
            nonlocal handler1_data
            handler1_data = data

        @service.event_handler("match.*")
        async def wildcard_handler(data: dict):
            nonlocal handler2_data
            handler2_data = data

        @service.event_handler("#")
        async def catch_all_handler(data: dict):
            nonlocal handler3_data
            handler3_data = data

        # Simulate message processing
        message = Mock()
        message_data = {"id": 999, "type": "match"}
        message.body = json.dumps(message_data).encode("utf-8")
        message.routing_key = "match.created"
        message.ack = AsyncMock()
        message.reject = AsyncMock()

        # Manually trigger the routing logic
        for event_pattern, handlers in service.event_handlers.items():
            if service._matches_pattern("match.created", event_pattern):
                for handler in handlers:
                    await service._process_message(message, handler)

        # All three handlers should have received the message
        assert handler1_data == message_data  # NOSONAR
        assert handler2_data == message_data  # NOSONAR
        assert handler3_data == message_data  # NOSONAR

    @pytest.mark.asyncio
    async def test_routing_with_no_matching_handlers(self, service):
        """Test routing when no handlers match the event."""

        @service.event_handler("match.created")
        async def handler(data: dict):
            """Temporary test handler."""
            pass

        message = Mock()
        message.body = json.dumps({"id": 111}).encode("utf-8")
        message.routing_key = "tournament.started"

        # Check that no handlers match
        matched = False
        for event_pattern in service.event_handlers.keys():
            if service._matches_pattern("tournament.started", event_pattern):
                matched = True
                break

        assert matched is False

    @pytest.mark.asyncio
    async def test_multiple_services_different_queues(self):
        """Test that different services have different queue names."""
        service1 = RabbitMQService(service_name="matches-service")
        service2 = RabbitMQService(service_name="tournaments-service")

        # Register handlers
        @service1.event_handler("match.created")
        async def handler1(data: dict):
            pass

        @service2.event_handler("match.created")
        async def handler2(data: dict):
            pass

        # Verify different queue names would be created
        queue_name1 = f"{service1.service_name}.events"
        queue_name2 = f"{service2.service_name}.events"

        assert queue_name1 == "matches-service.events"
        assert queue_name2 == "tournaments-service.events"
        assert queue_name1 != queue_name2
