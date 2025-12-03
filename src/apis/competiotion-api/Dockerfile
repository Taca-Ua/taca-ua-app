FROM python:3.11-slim

WORKDIR /app

<<<<<<< HEAD
COPY src/apis/competiotion-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install messaging package
COPY src/shared/taca-messaging /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging
COPY src/shared/ ./shared
COPY src/apis/competiotion-api .
=======
# copy requirements and app from repo-root paths (build context is repo root)
COPY src/apis/competiotion-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/apis/competiotion-api/ .
# copy shared utilities so `import shared` works
COPY src/shared/ ./shared
>>>>>>> 5b485845f7a2685576922cd49c1b4546fdcb65ab

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
