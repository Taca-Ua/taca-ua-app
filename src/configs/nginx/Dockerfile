FROM nginx:1.25-alpine

# Install OpenSSL for certificate generation
RUN apk add --no-cache openssl bash curl

# Copy certificate generation script and entrypoint
COPY generate_certs.sh /usr/local/bin/generate_certs.sh
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN sed -i 's/\r$//' /usr/local/bin/generate_certs.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh

# Make scripts executable
RUN chmod +x /usr/local/bin/generate_certs.sh && \
    chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
