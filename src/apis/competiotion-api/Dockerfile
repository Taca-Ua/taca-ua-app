FROM python:3.11-slim

WORKDIR /app

COPY src/apis/competiotion-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install messaging package
COPY src/shared/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

COPY src/apis/competiotion-api .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
