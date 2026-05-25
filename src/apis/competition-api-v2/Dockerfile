FROM python:3.11-slim

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Instalar dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. PRIMEIRO: Copiar os pacotes partilhados que o requirements precisa
# Criamos a estrutura de pastas temporária para o pip encontrar os locais
COPY src/shared/platform /tmp/platform
COPY src/shared/contracts /tmp/contracts

# 3. DEPOIS: Copiar e instalar o requirements
# Agora, se o requirements.txt procurar por /tmp/contracts/taca-events, ele já lá está!
COPY src/apis/competition-api-v2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Instalar os pacotes partilhados no Python (se não estiverem no requirements)
RUN pip install --no-cache-dir /tmp/platform/taca-messaging && \
    pip install --no-cache-dir /tmp/platform/taca-outbox

# 5. Copiar o resto do código da API
COPY src/apis/competition-api-v2 .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]