FROM python:3.11-slim

WORKDIR /app

COPY src/microservices/ranking-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install messaging package
COPY src/shared/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging
COPY src/shared/ ./shared
COPY src/microservices/ranking-service .

# Run migrations and start the service
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
