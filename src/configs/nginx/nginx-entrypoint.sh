#!/bin/sh
# Nginx entrypoint script (runs before nginx starts)
# Automatically selects HTTP or HTTPS configuration based on certificate availability

set -e

echo "=== Nginx Auto-Configuration ==="

# Define um valor padrão para FRONTEND_PORT caso não esteja definida (fallback para dev)
if [ -z "$FRONTEND_PORT" ]; then
    export FRONTEND_PORT=5173
    echo "ℹ️  FRONTEND_PORT not set, defaulting to 5173"
fi

# Replace environment variables in templates
if [ ! -z "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ]; then
    echo "📋 Configuring for domain: $DOMAIN using port: $FRONTEND_PORT"

    # Check if certificates exist
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        echo "✅ SSL certificates found - enabling HTTPS configuration"
        envsubst '${DOMAIN} ${FRONTEND_PORT}' < /etc/nginx/templates/nginx.conf.https > /etc/nginx/conf.d/default.conf
    else
        echo "⚠️  No SSL certificates found - using HTTP-only configuration"
        echo "   Certificates will be obtained automatically by certbot"
        envsubst '${DOMAIN} ${FRONTEND_PORT}' < /etc/nginx/templates/nginx.conf.http > /etc/nginx/conf.d/default.conf
    fi
else
    echo "⚠️  DOMAIN not set or set to localhost - using HTTP-only configuration (Port: $FRONTEND_PORT)"
    # Mesmo sem domínio, usamos envsubst para injetar a FRONTEND_PORT no config de fallback
    envsubst '${DOMAIN} ${FRONTEND_PORT}' < /etc/nginx/templates/nginx.conf.http > /etc/nginx/conf.d/default.conf
fi

# Copy SSL parameters
cp /etc/nginx/templates/ssl-params.conf /etc/nginx/conf.d/ssl-params.conf

echo "✅ Nginx configuration ready"

# Script exits here, nginx will be started by the main entrypoint