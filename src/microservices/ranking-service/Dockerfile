FROM python:3.11-slim

# Impede o Python de gerar ficheiros .pyc e garante que os logs saem em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 1. Instalar dependências de sistema (Essencial para evitar erro no pip install)
# build-essential e libpq-dev são necessários se usares PostgreSQL ou pacotes que compilam C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar dependências do Python (Requirements)
COPY src/microservices/ranking-service/requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Instalar pacotes partilhados (Caminhos corrigidos para platform/contracts)
# Messaging
COPY src/shared/platform/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

# Outbox
COPY src/shared/platform/taca-outbox /tmp/taca-outbox
RUN pip install --no-cache-dir /tmp/taca-outbox && rm -rf /tmp/taca-outbox

# Snapshots
COPY src/shared/contracts/taca-snapshots /tmp/taca-snapshots
RUN pip install --no-cache-dir /tmp/taca-snapshots && rm -rf /tmp/taca-snapshots

# Rebuild Framework
COPY src/shared/platform/taca-rebuild /tmp/taca-rebuild
RUN pip install --no-cache-dir /tmp/taca-rebuild && rm -rf /tmp/taca-rebuild

# 4. Copiar o código do serviço
COPY src/microservices/ranking-service .

# 5. Comando de inicialização
# Usamos sh -c para garantir que o alembic corre antes do servidor
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]