# Keycloak — Integração e configuração

Este documento descreve a configuração do Keycloak usada pelo projeto, como obter tokens para testes, e as alterações necessárias na aplicação para validar JWTs corretamente quando executada em containers Docker.

## Sumário

- [Visão geral](#visão-geral)
- [Instância e realm](#instância-e-realm)
- [Clientes e utilizadores](#clientes-e-utilizadores-de-teste)
- [Variáveis de ambiente](#variáveis-de-ambiente-principais)
- [Porquê duas URLs?](#porquê-duas-urls)
- [Implementação](#implementação-no-código-resumo)
- [Fluxos de autenticação](#fluxos-de-autenticação--exemplos)
- [Validação JWT](#como-funciona-a-validação-resumido)
- [Testes](#testes-e-verificação)
- [Boas práticas](#boas-práticas-e-notes-para-produção)
- [Troubleshooting](#resolução-de-problemas)

---

## Visão geral

O projeto usa Keycloak (imagem `quay.io/keycloak/keycloak:22.0.0`) como provedor OIDC e de RBAC. Os serviços validam tokens JWT emitidos pelo realm `taca-ua`.

---

## Instância e realm

- **Realm**: `taca-ua`
- **Keycloak (Docker)**: exposto externamente em `http://localhost/keycloak` através do proxy Nginx do ambiente de desenvolvimento.

---

## Clientes e utilizadores de teste

### Cliente (`api-client`)

- **Tipo**: Confidential
- **Direct Access Grants**: enabled (permite Resource Owner Password Credentials flow para testes)
- **Client Secret** (dev): `tJ5D1mOdUuDLFJhzYq950IOkFQZNN9AY` ⚠️ **Nunca comiter em produção**

### Utilizador de teste

- **Username**: `testuser`
- **Password**: `testpass123`

---

## Variáveis de ambiente (principais)

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `KEYCLOAK_URL` | URL pública (issuer dos tokens) | `http://localhost/keycloak` |
| `KEYCLOAK_INTERNAL_URL` | URL interna (para buscar JWKS dentro containers) | `http://keycloak:8080/keycloak` |
| `KEYCLOAK_REALM` | Nome do realm | `taca-ua` |
| `KEYCLOAK_CLIENT_ID` | ID do client | `api-client` |
| `KEYCLOAK_CLIENT_SECRET` | Secret do client (quando aplicável) | `tJ5D1mOdUuDLFJhzYq950IOkFQZNN9AY` |

**Nota**: No `docker-compose.yml`, adicionámos `KEYCLOAK_INTERNAL_URL=http://keycloak:8080/keycloak` aos serviços que validam tokens (ex.: `public-api`, microservices). Mantemos `KEYCLOAK_URL=http://localhost/keycloak` para validação do `iss` nos tokens emitidos.

---

## Porquê duas URLs?

Dentro de um container, `localhost` refere-se ao próprio container — não ao host nem ao serviço Keycloak.

### Issuer (externo)

- O token emitido por Keycloak tem como issuer a **URL pública** (visível para clientes), tipicamente `http://localhost/keycloak/realms/taca-ua`.
- Os serviços validam o `iss` do token contra `KEYCLOAK_URL` (URL externa).

### JWKS (interno)

- Para validar a assinatura do token, os serviços precisam do JWKS (JSON Web Key Set) do Keycloak.
- Buscar o JWKS por `http://localhost/...` dentro do container **falha**.
- Usamos `KEYCLOAK_INTERNAL_URL` (ex.: `http://keycloak:8080/keycloak`) para buscar `.../realms/taca-ua/protocol/openid-connect/certs` via rede Docker.

---

## Implementação no código (resumo)

### `src/shared/auth.py`

- Busca JWKS usando `KEYCLOAK_INTERNAL_URL`
- Verifica `iss` do token usando `KEYCLOAK_URL` (issuer externo)
- Faz caching simples do JWKS para reduzir chamadas
- Expõe `verify_token()` e `require_role()` usados como `Depends(...)` nos endpoints FastAPI

### Nginx

- Garantido que a rota `/api/public` **não é reescrita**, de modo que o caminho recebido pelo backend mantém o prefixo esperado (`/api/public/...`)

---

## Fluxos de autenticação — exemplos

### 1. Obter token (Direct Access Grant) — curl

```bash
curl -X POST \
  http://localhost/keycloak/realms/taca-ua/protocol/openid-connect/token \
  -d 'grant_type=password' \
  -d 'client_id=api-client' \
  -d 'client_secret=tJ5D1mOdUuDLFJhzYq950IOkFQZNN9AY' \
  -d 'username=testuser' \
  -d 'password=testpass123'
```

**Saída**: JSON com `access_token` (JWT), `refresh_token`, `expires_in`.

### 2. Obter token — PowerShell (Windows)

```powershell
$body = @{
  grant_type = 'password'
  client_id = 'api-client'
  client_secret = 'tJ5D1mOdUuDLFJhzYq950IOkFQZNN9AY'
  username = 'testuser'
  password = 'testpass123'
}

$response = Invoke-RestMethod -Method Post `
  -Uri 'http://localhost/keycloak/realms/taca-ua/protocol/openid-connect/token' `
  -Body $body

$response.access_token
```

### 3. Usar token para chamar endpoint protegido — curl

```bash
curl -X POST http://localhost/api/public/send-event?msg=Hello \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Onde `<ACCESS_TOKEN>` é o `access_token` retornado pelo Keycloak.

### 4. Usar token — PowerShell

```powershell
$headers = @{
  "Authorization" = "Bearer $($response.access_token)"
}

Invoke-RestMethod -Method Post `
  -Uri 'http://localhost/api/public/send-event?msg=Hello' `
  -Headers $headers
```

---

## Como funciona a validação (resumido)

1. **Serviço obtém** o header `Authorization: Bearer ...`.
2. **Extrai e decodifica** o JWT (sem validar) para ler `kid` (key id) do header.
3. **Busca o JWKS** em `KEYCLOAK_INTERNAL_URL/realms/<realm>/protocol/openid-connect/certs` e encontra a chave correspondente.
4. **Valida a assinatura** e as claims (`exp`, `iat`, `iss` == `KEYCLOAK_URL/realms/<realm>`).
5. **Se válido**, o endpoint prossegue; caso contrário retorna `401 Unauthorized`.

---

## Testes e verificação

### Descobrir endpoints públicos

```bash
curl http://localhost/api/public/openapi.json | jq '.paths | keys'
```

### Inspecionar um token (local, sem validação)

```bash
# Via jwt.io (online): https://jwt.io

# Ou em Python (local):
python -c "
import jwt, sys, json
token = sys.argv[1]
decoded = jwt.decode(token, options={'verify_signature': False})
print(json.dumps(decoded, indent=2))
" <TOKEN>
```

### Ver logs

```bash
docker-compose logs public-api
docker-compose logs nginx
docker-compose logs keycloak
```

---

## Boas práticas e notes para produção

- ⚠️ **Nunca comita** `client_secret` em texto no repositório.
- ✅ Em produção, use **HTTPS** e um domínio público para `KEYCLOAK_URL` (issuer). O issuer do token deve usar `https://...`.
- ✅ Use um mecanismo seguro para gerir segredos (Vault, Azure Key Vault, secrets em `docker-compose.yml`).
- ✅ Configure tempos de expiração e refresh tokens de acordo com a política da organização.
- ✅ Considere usar introspection endpoint para tokens opacos ou validação baseada em introspection quando aplicável.
- ✅ Implemente rate limiting no endpoint de token do Keycloak.

---

## Resolução de problemas

### 401 Unauthorized ao chamar endpoint protegido

- ✅ Verifique o header `Authorization` e se o token não expirou.
- ✅ Verifique se `KEYCLOAK_INTERNAL_URL` está correto e acessível a partir do container:

  ```bash
  docker-compose exec public-api curl -s http://keycloak:8080/keycloak/realms/taca-ua/protocol/openid-connect/certs
  ```

- ✅ Confira no Keycloak se o client está configurado como `confidential` e se o secret corresponde.

### 404 ao chamar endpoint que existe

- ✅ Verifique a configuração do Nginx; **não deve haver `rewrite` que remova** o prefixo `/api/public` quando o backend também o espera.
- ✅ Confirme que o backend realmente expõe a rota com o prefixo correto (ex.: `@app.post("/api/public/send-event")`).

### Erro na validação do `iss`

- ✅ Tokens emitidos pelo Keycloak terão `iss` baseado na URL pública do proxy. Confirme que `KEYCLOAK_URL` (variável usada para comparar o `iss`) corresponde **exatamente** ao issuer do token (sem trailing slash inconsistencies).

---

## Alterações aplicadas no repositório (resumo)

- ✅ Adicionada `KEYCLOAK_INTERNAL_URL` nas env vars do `docker-compose.yml` para serviços que validam JWTs.
- ✅ Atualizado `src/shared/auth.py` para usar `KEYCLOAK_INTERNAL_URL` ao buscar JWKS e `KEYCLOAK_URL` para validação do `iss`.
- ✅ Ajustado `src/configs/nginx/nginx.conf` para não reescrever o prefixo `/api/public`.

---

## Próximos passos (opcional)

- Adicionar scripts de exemplo para obter token e testar endpoints (`scripts/get_token.sh` / `scripts/get_token.ps1`).
- Implementar introspection do JWKS automatizada a partir dos containers.
- Configurar RBAC (`require_role`) em todos os microservices.
- Testar refresh tokens e expiração.

---

**Documento gerado pelo agente** — Se algo estiver diferente no teu ambiente (domains, ports, nomes), adapta os valores em `docker-compose.yml` e nas variáveis de ambiente dos serviços.
