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

# 1. PRE-STAGING: Copiar as pastas de pacotes partilhados
# O requirements.txt espera encontrar os pacotes em /tmp/contracts e /tmp/platform
COPY src/shared/contracts /tmp/contracts
COPY src/shared/platform /tmp/platform

# 2. Instalar dependências do requirements
COPY src/microservices/modalities-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar o código do serviço
COPY src/microservices/modalities-service .

# 4. Inicialização (Migrações + Servidor)
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000