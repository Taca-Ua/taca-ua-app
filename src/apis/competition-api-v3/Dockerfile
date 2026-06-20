FROM python:3.13-slim

# env cofiguration
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /app

# copy and install dependencies
COPY src/apis/competition-api-v3/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY src/apis/competition-api-v3 .

# run server
CMD ["sh" , "-c", "python manage.py migrate && python manage.py bootstrap_season && gunicorn --bind 0.0.0.0:8000 --access-logfile - --error-logfile - config.wsgi:application"]
