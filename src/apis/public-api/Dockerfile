FROM python:3.11-slim

WORKDIR /app

COPY src/apis/public-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install messaging package
COPY src/shared/rabbitmq-service /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

# Install shared modules package
COPY src/shared/read-model-shared /tmp/read-model-shared
RUN pip install --no-cache-dir /tmp/read-model-shared && rm -rf /tmp/read-model-shared

COPY src/apis/public-api .

# Run migrations and start the service
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
