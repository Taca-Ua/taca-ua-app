#!/bin/sh
# Entrypoint script for automated certificate generation
# This script runs once at startup to obtain certificates if they don't exist

set -e

echo "=== Certbot Initialization ==="

# Check if required environment variables are set
if [ -z "$DOMAIN" ]; then
    echo "ERROR: DOMAIN environment variable is not set"
    echo "Please set DOMAIN in your .env file (e.g., DOMAIN=example.com)"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    echo "ERROR: EMAIL environment variable is not set"
    echo "Please set EMAIL in your .env file (e.g., EMAIL=admin@example.com)"
    exit 1
fi

# Use staging server for testing if CERTBOT_STAGING=1
STAGING_ARG=""
if [ "$CERTBOT_STAGING" = "1" ]; then
    STAGING_ARG="--staging"
    echo "⚠️  Using Let's Encrypt STAGING server (test mode)"
else
    echo "✅ Using Let's Encrypt PRODUCTION server"
fi

# Check if certificate already exists
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "✅ Certificate for $DOMAIN already exists"
    echo "Switching to renewal mode..."
else
    echo "📋 Obtaining certificate for domain: $DOMAIN"
    echo "📧 Contact email: $EMAIL"

    # Wait for nginx to be ready
    echo "⏳ Waiting for nginx to be ready..."
    sleep 10

    # Test if nginx is responding
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if wget --spider --timeout=2 --tries=1 http://nginx/.well-known/acme-challenge/test 2>/dev/null || [ $? -eq 8 ]; then
            echo "✅ Nginx is ready"
            break
        fi
        attempt=$((attempt + 1))
        echo "Waiting for nginx... ($attempt/$max_attempts)"
        sleep 2
    done

    # Obtain certificate
    echo "🔐 Requesting certificate from Let's Encrypt..."
    certbot certonly \
        --webroot \
        -w /var/www/certbot \
        $STAGING_ARG \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        --rsa-key-size 4096 \
        --agree-tos \
        --no-eff-email \
        --non-interactive

    if [ $? -eq 0 ]; then
        echo "✅ Certificate obtained successfully!"

        # Signal nginx to reload
        echo "🔄 Signaling nginx to reload configuration..."
        # Find and reload nginx container
        if command -v docker >/dev/null 2>&1; then
            docker exec $(docker ps -q -f "ancestor=nginx:1.25-alpine" | head -n1) nginx -s reload 2>/dev/null || true
        fi
    else
        echo "❌ Failed to obtain certificate"
        echo "Common issues:"
        echo "  - Domain $DOMAIN does not point to this server"
        echo "  - Ports 80/443 are not accessible from the internet"
        echo "  - Firewall blocking connections"
        exit 1
    fi
fi

# Start the renewal loop
echo "🔁 Starting certificate renewal service..."
echo "Checking for renewal twice daily..."

# Trap TERM signal for graceful shutdown
trap exit TERM

while :; do
    # Renew certificates (only renews if within 30 days of expiry)
    certbot renew \
        --webroot \
        -w /var/www/certbot \
        --quiet \
        --deploy-hook "docker exec \$(docker ps -q -f 'ancestor=nginx:1.25-alpine' | head -n1) nginx -s reload 2>/dev/null || true"

    # Sleep for 12 hours
    sleep 12h & wait ${!}
done
