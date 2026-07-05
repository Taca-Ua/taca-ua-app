#!/bin/bash

# Certificate generation script for nginx SSL
set -e

DOMAIN="localhost"
CERT_DIR="/etc/nginx/certs"
KEY_FILE="${CERT_DIR}/key.pem"
CERT_FILE="${CERT_DIR}/cert.pem"

# Create certificate directory if it doesn't exist
mkdir -p "${CERT_DIR}"

# Check if certificates already exist
if [[ -f "${KEY_FILE}" && -f "${CERT_FILE}" ]]; then
    echo "SSL certificates already exist in ${CERT_DIR}"
    exit 0
fi

echo "Generating SSL certificates for ${DOMAIN}..."

# Generate private key
openssl genrsa -out "${KEY_FILE}" 2048

# Generate certificate
openssl req -new -x509 -key "${KEY_FILE}" -out "${CERT_FILE}" -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}" \
    -addext "subjectAltName=DNS:${DOMAIN},DNS:*.${DOMAIN},IP:127.0.0.1"

echo "SSL certificates generated successfully in ${CERT_DIR}"
echo "Key file: ${KEY_FILE}"
echo "Certificate file: ${CERT_FILE}"
