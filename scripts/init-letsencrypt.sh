#!/bin/bash

# Script para inicializar certificados Let's Encrypt com Certbot
# Uso: ./scripts/init-letsencrypt.sh <domain> <email>

if ! [ "$(id -u)" = 0 ]; then
    echo "Este script deve ser executado como root ou com sudo"
    exit 1
fi

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Uso: $0 <domain> <email>"
    echo "Exemplo: $0 exemplo.com admin@exemplo.com"
    exit 1
fi

DOMAIN=$1
EMAIL=$2
STAGING=${3:-0}  # Use staging server se 1

# Obter diretório do script e projeto
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

if [ "$STAGING" != "0" ]; then
    staging_arg="--staging"
    echo "⚠️  Usando servidor de staging do Let's Encrypt (para testes)"
else
    staging_arg=""
    echo "✅ Usando servidor de produção do Let's Encrypt"
fi

# Verificar se o Docker está rodando
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verificar se os serviços estão rodando
if ! docker-compose ps nginx | grep -q "Up"; then
    echo "⚠️  Nginx não está rodando. Iniciando serviços..."
    docker-compose up -d nginx
    sleep 5
fi

echo "📋 Obtendo certificado para domínio: $DOMAIN"
echo "📧 Email de contato: $EMAIL"

# Obter certificado
docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    --email $EMAIL \
    -d $DOMAIN \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal" certbot

if [ $? -eq 0 ]; then
    echo "✅ Certificado obtido com sucesso!"
    
    # Atualizar nginx.conf com o domínio
    echo "🔧 Atualizando configuração do Nginx..."
    
    # Usar script Python para atualizar nginx.conf
    if command -v python3 &> /dev/null; then
        python3 "$SCRIPT_DIR/update-nginx-ssl.py" "$DOMAIN"
    else
        echo "⚠️  Python3 não encontrado. Atualizando manualmente..."
        sed -i.bak "s/SEU_DOMINIO_AQUI/$DOMAIN/g" src/configs/nginx/nginx.conf
        echo "⚠️  Você precisa descomentar o bloco HTTPS manualmente no nginx.conf"
    fi
    
    # Recarregar nginx
    echo "🔄 Recarregando Nginx..."
    docker-compose exec nginx nginx -s reload
    
    echo ""
    echo "✅ Configuração concluída!"
    echo "🌐 Seu site deve estar acessível em https://$DOMAIN"
else
    echo "❌ Erro ao obter certificado"
    exit 1
fi

