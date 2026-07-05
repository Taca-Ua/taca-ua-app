FROM nginx:1.31-alpine

# Install OpenSSL for certificate generation
RUN apk add --no-cache gettext

# Copy certificate generation script and entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY templates/ etc/nginx/templates/

RUN sed -i 's/\r$//' /docker-entrypoint.sh

# Make scripts executable
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
