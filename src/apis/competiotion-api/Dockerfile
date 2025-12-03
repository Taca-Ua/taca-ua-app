FROM python:3.11-slim

WORKDIR /app

# copy requirements and app from repo-root paths (build context is repo root)
COPY src/apis/competiotion-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/apis/competiotion-api/ .
# copy shared utilities so `import shared` works
COPY src/shared/ ./shared

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
