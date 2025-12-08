# Configuração de TLS com Certbot

Este documento descreve como configurar certificados TLS/SSL usando Let's Encrypt e Certbot para o projeto taca-ua-app.

## Pré-requisitos

1. Um domínio válido apontando para o servidor onde a aplicação está rodando
2. Portas 80 e 443 abertas e acessíveis publicamente
3. Docker e Docker Compose instalados

## Configuração Inicial

### 1. Preparar o ambiente


```bash
docker-compose up -d nginx
```

### 2. Obter certificados TLS


```bash
sudo ./scripts/init-letsencrypt.sh exemplo.com admin@exemplo.com
```

Para testes (usando servidor de staging do Let's Encrypt):

```bash
sudo ./scripts/init-letsencrypt.sh exemplo.com admin@exemplo.com 1
```

O script irá:
- Obter certificados do Let's Encrypt
- Configurar automaticamente o nginx.conf para HTTPS
- Recarregar o nginx

### 3. Verificar certificados

Após a execução, os certificados aparecem em:

```
/etc/letsencrypt/live/<seu-dominio>/fullchain.pem
/etc/letsencrypt/live/<seu-dominio>/privkey.pem
```

### 4. Testar HTTPS

Acessamos o site via HTTPS:

```
https://nosso-domain.com # MUDAR NO FUTURO
```

O nginx irá automaticamente redirecionar todas as requisições HTTP (porta 80) para HTTPS (porta 443).

## Renovação Automática

Os certificados Let's Encrypt expiram a cada 90 dias. A renovação automática está configurada no serviço `certbot` do docker-compose.yml:

- O serviço certbot executa a verificação de renovação a cada 12 horas
- Se os certificados estiverem próximos do vencimento (30 dias), eles serão renovados automaticamente
- O nginx é recarregado automaticamente após a renovação

### Verificar renovação manualmente

Você pode testar a renovação manualmente:

```bash
docker-compose run --rm certbot renew --dry-run
```

## Estrutura de Arquivos

```
.
├── docker-compose.yml          # Configuração do certbot e volumes
├── src/
│   └── configs/
│       └── nginx/
│           ├── nginx.conf      # Configuração do nginx (HTTP + HTTPS)
│           └── ssl-params.conf # Parâmetros SSL recomendados
└── scripts/
    ├── init-letsencrypt.sh     # Script de inicialização
    ├── update-nginx-ssl.py     # Script para atualizar nginx.conf
    └── setup-ssl-nginx.sh      # Script auxiliar
```

## Volumes Docker

Os certificados são armazenados em volumes Docker:

- `certbot-www`: Diretório webroot para validação ACME
- `certbot-certs`: Certificados Let's Encrypt

## Configurações SSL

As configurações SSL seguem as recomendações do Let's Encrypt e Mozilla:

- TLS 1.2 e TLS 1.3
- Ciphers modernos e seguros
- OCSP stapling
- Headers de segurança (HSTS, X-Frame-Options, etc.)

## Troubleshooting

### Erro: "Failed to obtain certificate"

- Verifique se o domínio está apontando corretamente para o servidor
- Certifique-se de que as portas 80 e 443 estão acessíveis
- Verifique se o nginx está rodando e servindo o diretório `/.well-known/acme-challenge/`

### Certificados não são renovados

- Verifique os logs do container certbot:
  ```bash
  docker-compose logs certbot
  ```

### Nginx não carrega configuração SSL

- Verifique se o arquivo `nginx.conf` foi atualizado corretamente
- Teste a configuração:
  ```bash
  docker-compose exec nginx nginx -t
  ```
- Recarregue o nginx:
  ```bash
  docker-compose exec nginx nginx -s reload
  ```

### Usar certificados de staging para testes

Para evitar atingir os limites do Let's Encrypt durante testes:

```bash
sudo ./scripts/init-letsencrypt.sh exemplo.com admin@exemplo.com 1
```

Depois, quando estiver pronto para produção, remova o certificado de staging e obtenha um novo:

```bash
docker-compose run --rm certbot delete --cert-name exemplo.com
sudo ./scripts/init-letsencrypt.sh exemplo.com admin@exemplo.com
```

## Referências

- [Let's Encrypt](https://letsencrypt.org/)
- [Certbot Documentation](https://certbot.eff.org/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)

