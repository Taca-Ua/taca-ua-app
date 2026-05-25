#!/bin/bash
set -e

# Generate certificates if they don't exist
echo "Checking for SSL certificates..."
export CERT_DIR="/etc/nginx/certs"
/usr/local/bin/generate_certs.sh

# Start nginx
echo "Starting nginx..."
exec nginx -g "daemon off;"
