FROM python:3.11-slim

# Impedir buffers e ficheiros .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Dependências de sistema para Django/Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Dependências do Python (Caminho absoluto a partir da raiz)
COPY src/apis/competition-api-v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Instalar pacotes partilhados (Caminhos que confirmaste via ls)
COPY src/shared/platform/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

COPY src/shared/platform/taca-outbox /tmp/taca-outbox
RUN pip install --no-cache-dir /tmp/taca-outbox && rm -rf /tmp/taca-outbox

# 3. Código da API (Copia tudo o que está na pasta da API para o /app)
COPY src/apis/competition-api-v2 .

# Execução
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]