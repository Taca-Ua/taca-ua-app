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
COPY src/shared/platform/taca-logging /tmp/platform/taca-logging

# 2. Instalar dependências do requirements
COPY src/apis/public-api/requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copiar o código da API pública
COPY src/apis/public-api .

# 4. Inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
