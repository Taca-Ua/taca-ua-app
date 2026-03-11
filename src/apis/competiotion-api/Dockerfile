FROM python:3.11-slim

WORKDIR /app

# 1. Copiar primeiro TODA a pasta shared para o local que o requirements.txt espera (/tmp)
# O contexto do build é a raiz do projeto (.), por isso copiamos de src/shared
COPY src/shared /tmp

# 2. Agora copiar o requirements.txt
COPY src/apis/competiotion-api/requirements.txt .

# 3. Agora o pip já vai encontrar os caminhos /tmp/contracts/... e /tmp/platform/...
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar o resto do código da API
COPY src/apis/competiotion-api .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]