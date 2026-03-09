"""
Event handling for Ranking Service.
"""

from taca_messaging import RabbitMQService

rabbitmq_service = RabbitMQService(service_name="ranking-service")
