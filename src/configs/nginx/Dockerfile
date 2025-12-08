FROM nginx:1.25-alpine

# Install gettext for envsubst command
RUN apk add --no-cache gettext

# Create templates directory
RUN mkdir -p /etc/nginx/templates

# Copy nginx configuration templates
COPY src/configs/nginx/nginx.conf.http /etc/nginx/templates/nginx.conf.http
COPY src/configs/nginx/nginx.conf.https /etc/nginx/templates/nginx.conf.https
COPY src/configs/nginx/ssl-params.conf /etc/nginx/templates/ssl-params.conf

# Copy custom entrypoint script
COPY src/configs/nginx/nginx-entrypoint.sh /docker-entrypoint.d/40-auto-ssl-config.sh
RUN chmod +x /docker-entrypoint.d/40-auto-ssl-config.sh

# Remove default config (will be created by entrypoint)
RUN rm -f /etc/nginx/conf.d/default.conf

EXPOSE 80 443
