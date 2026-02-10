"""
Event handling for Matches Service.
"""

from taca_messaging import RabbitMQService

rabbitmq_service = RabbitMQService(service_name="matches-service")
