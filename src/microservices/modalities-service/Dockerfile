FROM python:3.11-slim

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema (necessário para psycopg2 e build de pacotes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. PRE-STAGING: Criar a estrutura exata que o seu requirements.txt espera
# O seu requirements usa /tmp/contracts e /tmp/platform
COPY src/shared/contracts /tmp/contracts
COPY src/shared/platform /tmp/platform

# 2. Instalar dependências
COPY src/microservices/modalities-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar o código do serviço
COPY src/microservices/modalities-service .

# 4. Comando de inicialização
# Nota: Alembic faz as migrações e o Uvicorn sobe o FastAPI
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000