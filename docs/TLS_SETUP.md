# Configuração de TLS/HTTPS com Certbot (Automática)

Este documento descreve como configurar certificados TLS/SSL usando Let's Encrypt e Certbot para o projeto taca-ua-app. A configuração é **totalmente automatizada** via Docker Compose - não é necessário executar scripts na máquina local.

## Pré-requisitos

1. **Domínio válido** apontando para o servidor onde a aplicação está rodando
2. **Portas 80 e 443** abertas e acessíveis publicamente na internet
3. **Docker e Docker Compose** instalados

## Configuração Inicial (Setup Simplificado)

### 1. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis necessárias:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:

```bash
# Seu domínio (obrigatório para HTTPS)
DOMAIN=seu-dominio.com

# Email para notificações do Let's Encrypt
CERTBOT_EMAIL=admin@seu-dominio.com

# 0 para produção, 1 para testes (staging)
CERTBOT_STAGING=0
```

**Importante:**
- Para **testes**, use `CERTBOT_STAGING=1` para evitar limites de requisições do Let's Encrypt
- Para **produção**, use `CERTBOT_STAGING=0` para obter certificados válidos

### 2. Iniciar a Aplicação

Execute apenas um comando:

```bash
docker-compose up -d
```

**O que acontece automaticamente:**

1. ✅ Nginx inicia em modo HTTP (para validação ACME)
2. ✅ Certbot aguarda o nginx estar pronto
3. ✅ Certbot solicita certificados ao Let's Encrypt
4. ✅ Nginx recarrega automaticamente com configuração HTTPS
5. ✅ Aplicação fica disponível via HTTPS

### 3. Verificar Status

Acompanhe o processo de obtenção de certificados:

```bash
# Ver logs do certbot
docker-compose logs -f certbot

# Ver logs do nginx
docker-compose logs -f nginx
```

### 4. Acessar a Aplicação

Após a conclusão (geralmente 30-60 segundos):

```
https://nosso-domain.com # MUDAR NO FUTURO
```

O nginx irá automaticamente redirecionar todas as requisições HTTP (porta 80) para HTTPS (porta 443).

## Renovação Automática

Os certificados Let's Encrypt expiram a cada 90 dias. A renovação automática está configurada no serviço `certbot` do docker-compose.yml:

- O serviço certbot executa a verificação de renovação a cada 12 horas
- Se os certificados estiverem próximos do vencimento (30 dias), eles serão renovados automaticamente
- O nginx é recarregado automaticamente após a renovação

### Verificar Status de Renovação

Para testar a renovação manualmente (dry-run):

```bash
docker-compose exec certbot certbot renew --dry-run
```

Para forçar renovação (somente para testes):

```bash
docker-compose exec certbot certbot renew --force-renewal
docker-compose exec nginx nginx -s reload
```

## Estrutura de Arquivos

```
.
├── .env                        # Variáveis de ambiente (DOMAIN, CERTBOT_EMAIL)
├── .env.example               # Template de configuração
├── docker-compose.yml         # Orquestração dos serviços
├── src/
│   └── configs/
│       ├── certbot/
│       │   └── init-certbot.sh         # Script de inicialização automática
│       └── nginx/
│           ├── Dockerfile              # Build customizado do nginx
│           ├── nginx-entrypoint.sh     # Entrypoint para auto-configuração
│           ├── nginx.conf.http         # Config HTTP (pré-certificados)
│           ├── nginx.conf.https        # Config HTTPS (pós-certificados)
│           └── ssl-params.conf         # Parâmetros SSL recomendados
```

## Volumes Docker

Os certificados são persistidos em volumes Docker:

- **`certbot-www`**: Diretório webroot para validação ACME (`.well-known/acme-challenge/`)
- **`certbot-certs`**: Certificados Let's Encrypt (`/etc/letsencrypt`)

Para fazer backup dos certificados:

```bash
docker run --rm -v taca-ua-app_certbot-certs:/certs -v $(pwd):/backup alpine tar czf /backup/certificates-backup.tar.gz -C /certs .
```

Para restaurar certificados:

```bash
docker run --rm -v taca-ua-app_certbot-certs:/certs -v $(pwd):/backup alpine tar xzf /backup/certificates-backup.tar.gz -C /certs
```

## Configurações SSL

As configurações SSL seguem as recomendações do Let's Encrypt e Mozilla:

- ✅ **TLS 1.2 e TLS 1.3** (versões seguras)
- ✅ **Ciphers modernos** (ECDHE, CHACHA20, GCM)
- ✅ **OCSP Stapling** (performance e privacidade)
- ✅ **Security Headers**:
  - HSTS (Strict-Transport-Security)
  - X-Frame-Options (proteção contra clickjacking)
  - X-Content-Type-Options (proteção contra MIME sniffing)
  - X-XSS-Protection

## Troubleshooting

### ❌ Erro: "Failed to obtain certificate"

**Possíveis causas:**

1. **Domínio não está apontando para o servidor**
   ```bash
   # Verificar DNS
   nslookup seu-dominio.com
   dig seu-dominio.com
   ```

2. **Portas 80/443 não estão acessíveis**
   ```bash
   # Testar conectividade externa
   curl -I http://seu-dominio.com/.well-known/acme-challenge/test
   ```

3. **Firewall bloqueando conexões**
   - Windows: Verifique Windows Firewall
   - Linux: Verifique `iptables` ou `ufw`
   - Cloud: Verifique Security Groups (AWS/Azure/GCP)

**Solução:**
```bash
# Ver logs detalhados do certbot
docker-compose logs certbot

# Testar com staging primeiro
# Edite .env: CERTBOT_STAGING=1
docker-compose down
docker volume rm taca-ua-app_certbot-certs
docker-compose up -d
```

### ❌ Certificados não são renovados

```bash
# Verificar logs do certbot
docker-compose logs certbot

# Testar renovação manual
docker-compose exec certbot certbot renew --dry-run

# Verificar data de expiração
docker-compose exec certbot certbot certificates
```

### ❌ Nginx não aceita configuração SSL

```bash
# Testar configuração do nginx
docker-compose exec nginx nginx -t

# Ver logs do nginx
docker-compose logs nginx

# Recarregar configuração
docker-compose exec nginx nginx -s reload
```

### ⚠️ Rate Limit do Let's Encrypt

Let's Encrypt tem limites de requisições:
- **50 certificados por domínio por semana**
- **5 falhas de validação por hora**

**Solução:** Use staging para testes (`CERTBOT_STAGING=1`)

### 🔄 Recriar Certificados do Zero

```bash
# Parar serviços
docker-compose down

# Remover certificados antigos
docker volume rm taca-ua-app_certbot-certs taca-ua-app_certbot-www

# Reiniciar
docker-compose up -d
```

## Desenvolvimento Local (sem HTTPS)

Para desenvolvimento local sem domínio válido:

```bash
# No arquivo .env
DOMAIN=localhost
CERTBOT_EMAIL=admin@localhost
```

O nginx funcionará apenas em **modo HTTP** (porta 80) pois certificados Let's Encrypt requerem um domínio público válido.

## Migração de Staging para Produção

Se você testou com certificados de staging e quer migrar para produção:

```bash
# 1. Parar serviços
docker-compose down

# 2. Remover certificados de staging
docker volume rm taca-ua-app_certbot-certs

# 3. Atualizar .env
CERTBOT_STAGING=0

# 4. Reiniciar com certificados de produção
docker-compose up -d
```

## Como Funciona

### Fluxo de Inicialização

1. **Nginx inicia** com configuração HTTP-only (`nginx.conf.http`)
2. **Certbot verifica** se já existem certificados
3. **Se não existirem certificados**:
   - Aguarda nginx estar pronto (até 60 segundos)
   - Solicita certificados via challenge HTTP-01 (`.well-known/acme-challenge/`)
   - Sinaliza nginx para recarregar
4. **Nginx recarrega** e detecta certificados, muda para `nginx.conf.https`
5. **HTTPS ativo** com redirecionamento automático HTTP → HTTPS

### Fluxo de Renovação

1. A cada **12 horas**, certbot verifica expiração
2. Se faltarem **menos de 30 dias**, inicia renovação
3. Após renovação bem-sucedida, recarrega nginx
4. **Zero downtime** durante o processo

## Arquitetura

```
┌─────────────────────────────────────────────┐
│         Internet (Cliente)                   │
└────────────┬───────────────────────────────┘
             │
             │ HTTP (80) / HTTPS (443)
             │
             ▼
┌─────────────────────────────────────────────┐
│         Nginx Reverse Proxy                  │
│  - Auto-detecção de certificados             │
│  - HTTP → HTTPS redirect                     │
│  - TLS termination                           │
└────┬────────────────────────────────────┬───┘
     │                                     │
     │                                     │ /.well-known/acme-challenge/
     │                                     │
     │                                     ▼
     │                           ┌────────────────┐
     │                           │    Certbot     │
     │                           │  - Validação   │
     │                           │  - Renovação   │
     │                           └────────────────┘
     │
     ├─────► Public Website (5173)
     ├─────► Admin Panel (5173)
     ├─────► Competition API (8000)
     ├─────► Public API (8000)
     ├─────► Keycloak (8080)
     └─────► Grafana (3000)
```

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória | Exemplo |
|----------|-----------|-------------|---------|
| `DOMAIN` | Domínio da aplicação | ✅ Sim | `example.com` |
| `CERTBOT_EMAIL` | Email para notificações | ✅ Sim | `admin@example.com` |
| `CERTBOT_STAGING` | Modo staging (0=prod, 1=test) | ❌ Não (default: 0) | `0` |

## Segurança

### Certificados

- ✅ **RSA 4096-bit** keys (máxima compatibilidade e segurança)
- ✅ Certificados válidos por **90 dias**
- ✅ Renovação automática **30 dias antes** da expiração
- ✅ OCSP Stapling para verificação de revogação

### Headers de Segurança

Configurados automaticamente em `ssl-params.conf`:

```nginx
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### Protocolos e Ciphers

- ✅ **TLS 1.2 e TLS 1.3** apenas (TLS 1.0/1.1 desabilitados)
- ✅ **Ciphers modernos** priorizando perfect forward secrecy (ECDHE)
- ✅ Compatível com navegadores modernos (últimos 2 anos)

## Referências

- [Let's Encrypt](https://letsencrypt.org/) - Autoridade Certificadora gratuita
- [Certbot Documentation](https://certbot.eff.org/) - Cliente ACME oficial
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html) - Documentação oficial
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) - Gerador de configs SSL
- [SSL Labs](https://www.ssllabs.com/ssltest/) - Teste a qualidade do seu SSL
