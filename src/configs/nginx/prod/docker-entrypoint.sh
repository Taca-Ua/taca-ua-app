#!/bin/sh
set -e

envsubst '${DOMAIN}' \
    < /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
