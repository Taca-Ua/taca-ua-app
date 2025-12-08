#!/bin/sh
# Nginx entrypoint script (runs before nginx starts)
# Automatically selects HTTP or HTTPS configuration based on certificate availability
# This script is executed by the nginx docker-entrypoint.d mechanism

set -e

echo "=== Nginx Auto-Configuration ==="

# Replace environment variables in templates
if [ ! -z "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ]; then
    echo "📋 Configuring for domain: $DOMAIN"

    # Check if certificates exist
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        echo "✅ SSL certificates found - enabling HTTPS configuration"
        envsubst '${DOMAIN}' < /etc/nginx/templates/nginx.conf.https > /etc/nginx/conf.d/default.conf
    else
        echo "⚠️  No SSL certificates found - using HTTP-only configuration"
        echo "   Certificates will be obtained automatically by certbot"
        echo "   Nginx will be reloaded with HTTPS after certificate generation"
        envsubst '${DOMAIN}' < /etc/nginx/templates/nginx.conf.http > /etc/nginx/conf.d/default.conf
    fi
else
    echo "⚠️  DOMAIN not set or set to localhost - using HTTP-only configuration"
    cp /etc/nginx/templates/nginx.conf.http /etc/nginx/conf.d/default.conf
fi

# Copy SSL parameters
cp /etc/nginx/templates/ssl-params.conf /etc/nginx/conf.d/ssl-params.conf

echo "✅ Nginx configuration ready"

# Script exits here, nginx will be started by the main entrypoint
