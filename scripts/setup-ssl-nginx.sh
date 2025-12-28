#!/bin/bash

# Script auxiliar para configurar automaticamente o nginx.conf com HTTPS
# Uso: ./scripts/setup-ssl-nginx.sh <domain>

if [ -z "$1" ]; then
    echo "Uso: $0 <domain>"
    echo "Exemplo: $0 exemplo.com"
    exit 1
fi

DOMAIN=$1
NGINX_CONF="src/configs/nginx/nginx.conf"
TEMP_FILE=$(mktemp)

echo "🔧 Configurando Nginx para usar certificados SSL..."

# Ler o arquivo e processar
python3 << EOF
import re
import sys

with open('$NGINX_CONF', 'r') as f:
    content = f.read()

# Substituir placeholder do domínio
content = content.replace('SEU_DOMINIO_AQUI', '$DOMAIN')

# Descomentar bloco HTTPS
# Encontrar o bloco comentado do servidor HTTPS
https_block_pattern = r'# server \{[^#]*listen 443 ssl http2;[^#]*server_name[^#]*\};'
https_block_match = re.search(r'# server \{[^#]*listen 443 ssl http2;[^#]*server_name[^#]*;[^#]*ssl_certificate[^#]*;[^#]*ssl_certificate_key[^#]*;[^#]*include[^#]*;.*?# \}', content, re.DOTALL)

if https_block_match:
    # Descomentar o bloco
    https_block = https_block_match.group(0)
    uncommented = re.sub(r'^# ', '', https_block, flags=re.MULTILINE)
    uncommented = re.sub(r'^    # ', '    ', uncommented, flags=re.MULTILINE)
    content = content.replace(https_block, uncommented)

# Descomentar redirecionamento HTTP->HTTPS
content = re.sub(r'# return 301 https://', 'return 301 https://', content)

# Comentar configuração HTTP temporária após descomentar redirecionamento
# Isso requer lógica mais complexa, então vamos manter a abordagem manual

with open('$NGINX_CONF', 'w') as f:
    f.write(content)

print("✅ Configuração atualizada!")
EOF

if [ $? -eq 0 ]; then
    echo "🔄 Recarregando Nginx..."
    docker-compose exec nginx nginx -s reload 2>/dev/null || echo "⚠️  Execute 'docker-compose exec nginx nginx -s reload' manualmente"
    echo "✅ Concluído!"
else
    echo "❌ Erro ao atualizar configuração"
    exit 1
fi

