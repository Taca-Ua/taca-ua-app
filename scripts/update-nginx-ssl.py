#!/usr/bin/env python3
"""
Script para atualizar configuração do Nginx com certificados SSL
"""
import re
import sys

def update_nginx_conf(domain, nginx_conf_path='src/configs/nginx/nginx.conf'):
    """Atualiza nginx.conf para habilitar HTTPS"""
    
    with open(nginx_conf_path, 'r') as f:
        content = f.read()
    
    # Substituir placeholder do domínio
    content = content.replace('SEU_DOMINIO_AQUI', domain)
    
    # Descomentar redirecionamento HTTP->HTTPS
    content = re.sub(
        r'#\s*return 301 https://\$host\$request_uri;',
        'return 301 https://$host$request_uri;',
        content
    )
    
    # Comentar as localizações HTTP temporárias (manter apenas ACME challenge)
    # Criar novo bloco HTTP apenas com ACME challenge
    http_block_new = f"""# Servidor HTTP - serve desafio ACME e redireciona para HTTPS
server {{
    listen 80;
    server_name _;

    # Desafio ACME do Let's Encrypt (certbot)
    location /.well-known/acme-challenge/ {{
        root /var/www/certbot;
    }}

    # Redirecionar todo o resto para HTTPS
    location / {{
        return 301 https://$host$request_uri;
    }}
}}"""
    
    # Substituir o bloco HTTP antigo
    http_block_pattern = r'# Servidor HTTP.*?location /keycloak/.*?proxy_buffering off;\s*\}}'
    content = re.sub(http_block_pattern, http_block_new, content, flags=re.DOTALL)
    
    # Descomentar bloco HTTPS
    https_template = f"""
# Servidor HTTPS
server {{
    listen 443 ssl http2;
    server_name {domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    include /etc/nginx/conf.d/ssl-params.conf;

    location /admin/ {{
        proxy_pass http://admin-panel:5173/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_buffering off;
    }}

    location / {{
        proxy_pass http://public-website:5173/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_buffering off;
    }}

    location /api/competition/ {{
        proxy_pass http://competition-api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /api/ {{
        proxy_pass http://public-api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /keycloak/ {{
        proxy_pass http://keycloak:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }}
}}"""
    
    # Remover bloco HTTPS comentado e adicionar novo
    https_comment_pattern = r'# Servidor HTTPS.*?#\s*\}$'
    if re.search(https_comment_pattern, content, flags=re.DOTALL):
        content = re.sub(https_comment_pattern, https_template, content, flags=re.DOTALL)
    else:
        # Adicionar no final se não existir
        content = content.rstrip() + https_template + '\n'
    
    # Escrever arquivo atualizado
    with open(nginx_conf_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Configuração do Nginx atualizada para domínio: {domain}")
    print("✅ HTTPS habilitado e redirecionamento HTTP->HTTPS configurado")
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 update-nginx-ssl.py <domain>")
        print("Exemplo: python3 update-nginx-ssl.py exemplo.com")
        sys.exit(1)
    
    domain = sys.argv[1]
    update_nginx_conf(domain)
