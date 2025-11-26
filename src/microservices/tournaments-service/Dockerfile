FROM python:3.11-slim

WORKDIR /app

# Install messaging package
COPY src/shared /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

COPY src/microservices/tournaments-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/microservices/tournaments-service .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
