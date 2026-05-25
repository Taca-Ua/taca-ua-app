FROM python:3.11-slim

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. PRE-STAGING: Satisfazer as dependências do requirements.txt
# O seu requirements espera /tmp/contracts e /tmp/platform
COPY src/shared/contracts /tmp/contracts
COPY src/shared/platform /tmp/platform

# 2. Instalar dependências
COPY src/microservices/read-model-updater/requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copiar o código do serviço
COPY src/microservices/read-model-updater .

# 4. Inicialização
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000