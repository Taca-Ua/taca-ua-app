FROM python:3.11-slim

WORKDIR /app

<<<<<<< HEAD
COPY src/apis/public-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install messaging package
COPY src/shared/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging
=======
# copy requirements and app from repo-root paths (build context is repo root)
COPY src/apis/public-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/apis/public-api/ .
# copy shared utilities so `import shared` works
COPY src/shared/ ./shared
>>>>>>> 5b485845f7a2685576922cd49c1b4546fdcb65ab

# Install shared modules package
COPY src/shared/read-model-shared /tmp/read-model-shared
RUN pip install --no-cache-dir /tmp/read-model-shared && rm -rf /tmp/read-model-shared
COPY src/shared/ ./shared
COPY src/apis/public-api .

# Run migrations and start the service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
