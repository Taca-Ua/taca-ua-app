FROM python:3.11-slim

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema para compilação e Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. PRE-STAGING: Satisfazer as dependências do requirements.txt
# Copiamos as pastas inteiras para garantir que taca-events, taca-logging, etc.
COPY src/shared/contracts /tmp/contracts
COPY src/shared/platform /tmp/platform

# 2. Instalar dependências do Python
COPY src/microservices/tournaments-service/requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copiar o código do serviço
COPY src/microservices/tournaments-service .

# 4. Inicialização (Migrações + Uvicorn)
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000