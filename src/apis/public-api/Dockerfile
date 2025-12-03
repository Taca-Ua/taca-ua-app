FROM python:3.11-slim

WORKDIR /app

# copy requirements and app from repo-root paths (build context is repo root)
COPY src/apis/public-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/apis/public-api/ .
# copy shared utilities so `import shared` works
COPY src/shared/ ./shared

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
