#!/bin/bash

# Script para verificar se a configuração TLS está funcionando corretamente
# Uso: ./scripts/verify-tls-setup.sh [domain]

DOMAIN=${1:-""}
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Verificando configuração TLS/Certbot..."
echo ""

# 1. Verificar se Docker está rodando
echo "1️⃣ Verificando Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Docker está rodando${NC}"
fi
echo ""

# 2. Verificar se containers estão rodando
echo "2️⃣ Verificando containers..."
if docker-compose ps nginx | grep -q "Up"; then
    echo -e "${GREEN}✅ Nginx está rodando${NC}"
else
    echo -e "${RED}❌ Nginx não está rodando${NC}"
    echo "   Execute: docker-compose up -d nginx"
fi

if docker-compose ps certbot | grep -q "Up"; then
    echo -e "${GREEN}✅ Certbot está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  Certbot não está rodando (isso é normal se você ainda não obteve certificados)${NC}"
fi
echo ""

# 3. Verificar se volumes existem
echo "3️⃣ Verificando volumes Docker..."
if docker volume ls | grep -q "taca-ua-app_certbot-www"; then
    echo -e "${GREEN}✅ Volume certbot-www existe${NC}"
else
    echo -e "${YELLOW}⚠️  Volume certbot-www não encontrado${NC}"
fi

if docker volume ls | grep -q "taca-ua-app_certbot-certs"; then
    echo -e "${GREEN}✅ Volume certbot-certs existe${NC}"
else
    echo -e "${YELLOW}⚠️  Volume certbot-certs não encontrado${NC}"
fi
echo ""

# 4. Verificar configuração do Nginx
echo "4️⃣ Verificando configuração do Nginx..."
if docker-compose exec -T nginx nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✅ Configuração do Nginx é válida${NC}"
else
    echo -e "${RED}❌ Erro na configuração do Nginx${NC}"
    docker-compose exec nginx nginx -t
fi
echo ""

# 5. Verificar certificados (se domínio foi fornecido)
if [ -n "$DOMAIN" ]; then
    echo "5️⃣ Verificando certificados para domínio: $DOMAIN"
    
    # Verificar se certificados existem no volume
    CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    
    if docker-compose run --rm --no-deps certbot ls "$CERT_PATH" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Certificados encontrados${NC}"
        
        # Verificar validade do certificado
        CERT_INFO=$(docker-compose run --rm --no-deps certbot openssl x509 -in "$CERT_PATH" -noout -dates 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "   Informações do certificado:"
            echo "$CERT_INFO" | sed 's/^/   /'
            
            # Verificar se está próximo do vencimento
            EXPIRY_DATE=$(echo "$CERT_INFO" | grep "notAfter" | cut -d= -f2)
            EXPIRY_EPOCH=$(date -j -f "%b %d %H:%M:%S %Y %Z" "$EXPIRY_DATE" +%s 2>/dev/null || date -d "$EXPIRY_DATE" +%s 2>/dev/null)
            NOW_EPOCH=$(date +%s)
            DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
            
            if [ $DAYS_LEFT -gt 30 ]; then
                echo -e "   ${GREEN}✅ Certificado válido por mais $DAYS_LEFT dias${NC}"
            elif [ $DAYS_LEFT -gt 0 ]; then
                echo -e "   ${YELLOW}⚠️  Certificado expira em $DAYS_LEFT dias${NC}"
            else
                echo -e "   ${RED}❌ Certificado expirado!${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Certificados não encontrados para $DOMAIN${NC}"
        echo "   Execute: sudo ./scripts/init-letsencrypt.sh $DOMAIN seu-email@exemplo.com"
    fi
    echo ""
fi

# 6. Verificar se porta 80 está acessível
echo "6️⃣ Verificando portas..."
if netstat -an 2>/dev/null | grep -q ":80.*LISTEN" || lsof -i :80 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Porta 80 está em uso${NC}"
else
    echo -e "${YELLOW}⚠️  Porta 80 não está em uso (pode ser normal se estiver usando Docker)${NC}"
fi

if netstat -an 2>/dev/null | grep -q ":443.*LISTEN" || lsof -i :443 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Porta 443 está em uso${NC}"
else
    echo -e "${YELLOW}⚠️  Porta 443 não está em uso (isso é normal se HTTPS ainda não estiver configurado)${NC}"
fi
echo ""

# 7. Verificar logs do Certbot
echo "7️⃣ Últimas entradas do log do Certbot:"
docker-compose logs --tail=10 certbot 2>/dev/null || echo "   Nenhum log disponível"
echo ""

# 8. Teste de conectividade HTTP (se domínio fornecido)
if [ -n "$DOMAIN" ]; then
    echo "8️⃣ Testando conectividade..."
    
    # Testar HTTP
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 5 "http://$DOMAIN/.well-known/acme-challenge/test" 2>/dev/null)
    if [ "$HTTP_STATUS" = "404" ] || [ "$HTTP_STATUS" = "403" ]; then
        echo -e "${GREEN}✅ HTTP está acessível (status: $HTTP_STATUS)${NC}"
    elif [ "$HTTP_STATUS" = "000" ]; then
        echo -e "${RED}❌ Não foi possível conectar via HTTP${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP retornou status: $HTTP_STATUS${NC}"
    fi
    
    # Testar HTTPS
    HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 5 "https://$DOMAIN" 2>/dev/null)
    if [ "$HTTPS_STATUS" = "200" ] || [ "$HTTPS_STATUS" = "301" ] || [ "$HTTPS_STATUS" = "302" ]; then
        echo -e "${GREEN}✅ HTTPS está acessível (status: $HTTPS_STATUS)${NC}"
        
        # Verificar certificado via curl
        CERT_DETAILS=$(curl -s -v "https://$DOMAIN" 2>&1 | grep -i "subject:\|issuer:\|expire date")
        if [ -n "$CERT_DETAILS" ]; then
            echo "   Detalhes do certificado:"
            echo "$CERT_DETAILS" | sed 's/^/   /'
        fi
    elif [ "$HTTPS_STATUS" = "000" ]; then
        echo -e "${YELLOW}⚠️  HTTPS não está acessível ou certificados não foram configurados${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS retornou status: $HTTPS_STATUS${NC}"
    fi
    echo ""
fi

# 9. Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Resumo da Verificação"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$DOMAIN" ]; then
    echo ""
    echo "Para testar manualmente:"
    echo "  HTTP:  curl -I http://$DOMAIN"
    echo "  HTTPS: curl -I https://$DOMAIN"
    echo ""
    echo "Para verificar certificado SSL online:"
    echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
fi

echo ""
echo "Para ver logs em tempo real:"
echo "  docker-compose logs -f nginx certbot"
echo ""

