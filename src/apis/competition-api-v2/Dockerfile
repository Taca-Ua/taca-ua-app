FROM python:3.11-slim

# Dependências de sistema para Django/Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Dependências do Python
COPY src/apis/competition-api-v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Instalar pacotes partilhados (Caminhos específicos que confirmamos no ls)
COPY src/shared/platform/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

COPY src/shared/platform/taca-outbox /tmp/taca-outbox
RUN pip install --no-cache-dir /tmp/taca-outbox && rm -rf /tmp/taca-outbox

# 3. Código da API
COPY src/apis/competition-api-v2 .

# Em produção usamos gunicorn ou uvicorn, mas mantendo o teu padrão:
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]