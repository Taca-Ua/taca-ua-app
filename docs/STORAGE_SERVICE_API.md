# Storage Service API Documentation

## Visão Geral

O **Storage Service** é um microserviço isolado e genérico responsável pelo armazenamento de arquivos com deduplicação automática baseada em hash SHA256. Utiliza MinIO como backend de armazenamento e oferece uma API REST simples para upload, download, e gerenciamento de arquivos.

**Base URL:** `http://storage-service:8000` (interno) ou `http://localhost:8080` (desenvolvimento)

**Versão:** 1.0.0

---

## Características

- ✅ **Deduplicação Automática:** Arquivos idênticos são armazenados apenas uma vez
- ✅ **Multi-Bucket:** Suporte para organização em múltiplos buckets
- ✅ **Metadados Customizados:** Armazenamento de informações adicionais
- ✅ **URLs Presigned:** Geração de URLs temporárias para acesso seguro
- ✅ **Suporte a Qualquer Tipo de Arquivo:** PDF, imagens, documentos, etc.
- ✅ **Health Check:** Monitoramento de saúde do serviço

---

## Endpoints REST

### 1. Health Check

Verifica se o serviço está funcionando corretamente.

#### `GET /health`

**Resposta de Sucesso:** `200 OK`

```json
{
  "status": "healthy",
  "service": "storage-service"
}
```

**Exemplo:**
```bash
curl http://localhost:8080/health
```

---

### 2. Upload de Arquivo

Faz upload de um arquivo para o storage com deduplicação automática.

#### `POST /upload`

**Content-Type:** `multipart/form-data`

**Parâmetros:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `file` | File | Sim | Arquivo a ser enviado |
| `bucket` | String | Não | Nome do bucket (default: "files") |
| `metadata` | JSON String | Não | Metadados customizados em formato JSON |

**Resposta de Sucesso:** `200 OK`

```json
{
  "success": true,
  "hash": "9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d",
  "filename": "9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf",
  "original_filename": "documento.pdf",
  "url": "http://localhost:9000/regulations/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "bucket": "regulations",
  "already_exists": false
}
```

**Campos da Resposta:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `success` | Boolean | Indica se o upload foi bem-sucedido |
| `hash` | String | Hash SHA256 do arquivo |
| `filename` | String | Nome único do arquivo (hash + extensão) |
| `original_filename` | String | Nome original do arquivo |
| `url` | String | URL pública para acesso ao arquivo |
| `size` | Integer | Tamanho do arquivo em bytes |
| `content_type` | String | MIME type do arquivo |
| `bucket` | String | Nome do bucket onde foi armazenado |
| `already_exists` | Boolean | `true` se o arquivo já existia (deduplicação) |

**Resposta de Erro:** `500 Internal Server Error`

```json
{
  "success": false,
  "error": "Error message"
}
```

**Exemplos:**

```bash
# Upload simples
curl -X POST http://localhost:8080/upload \
  -F "file=@documento.pdf" \
  -F "bucket=regulations"

# Upload com metadados
curl -X POST http://localhost:8080/upload \
  -F "file=@foto.jpg" \
  -F "bucket=images" \
  -F 'metadata={"user_id":"123","category":"profile","uploaded_at":"2024-12-09"}'
```

**Validações:**
- O arquivo não pode estar vazio
- Metadados devem ser JSON válido (se fornecidos)

---

### 3. Download de Arquivo

Faz download de um arquivo pelo nome.

#### `GET /download/{filename}`

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `filename` | String | Nome único do arquivo (hash + extensão) |

**Query Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `bucket` | String | Não | Nome do bucket (default: "files") |

**Resposta de Sucesso:** `200 OK`

Retorna o conteúdo do arquivo com o `Content-Type` apropriado e header `Content-Disposition` para download.

**Resposta de Erro:** `404 Not Found`

```json
{
  "detail": "File not found"
}
```

**Exemplos:**

```bash
# Download simples
curl http://localhost:8080/download/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf \
  --output arquivo.pdf

# Download de bucket específico
curl "http://localhost:8080/download/abc123.jpg?bucket=images" \
  --output foto.jpg
```

---

### 4. Informações do Arquivo

Obtém metadados de um arquivo.

#### `GET /info/{filename}`

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `filename` | String | Nome único do arquivo |

**Query Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `bucket` | String | Não | Nome do bucket (default: "files") |

**Resposta de Sucesso:** `200 OK`

```json
{
  "filename": "9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "last_modified": "2024-12-09T10:30:00+00:00",
  "metadata": {
    "original_filename": "documento.pdf",
    "user_id": "123",
    "category": "regulation"
  },
  "bucket": "regulations"
}
```

**Resposta de Erro:** `404 Not Found`

```json
{
  "detail": "File not found"
}
```

**Exemplo:**

```bash
curl "http://localhost:8080/info/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf?bucket=regulations"
```

---

### 5. Verificar Existência de Arquivo

Verifica se um arquivo com determinado hash existe no storage.

#### `GET /exists/{file_hash}`

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `file_hash` | String | Hash SHA256 do arquivo |

**Query Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `extension` | String | Não | Extensão do arquivo (ex: ".pdf") |
| `bucket` | String | Não | Nome do bucket (default: "files") |

**Resposta de Sucesso:** `200 OK`

```json
{
  "exists": true,
  "hash": "9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d"
}
```

**Exemplo:**

```bash
curl "http://localhost:8080/exists/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d?extension=.pdf&bucket=regulations"
```

**Nota:** Use aspas na URL para evitar problemas com o caractere `&` no terminal.

---

### 6. Obter URL Presigned

Gera uma URL temporária com acesso autenticado ao arquivo.

#### `GET /presigned/{filename}`

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `filename` | String | Nome único do arquivo |

**Query Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `bucket` | String | Não | Nome do bucket (default: "files") |
| `expiry_hours` | Integer | Não | Horas até expiração (default: 1) |

**Resposta de Sucesso:** `200 OK`

```json
{
  "url": "http://localhost:9000/regulations/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
  "expires_in_hours": 2
}
```

**Resposta de Erro:** `404 Not Found`

```json
{
  "detail": "File not found"
}
```

**Exemplo:**

```bash
curl "http://localhost:8080/presigned/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf?bucket=regulations&expiry_hours=2"
```

**Uso:**
- A URL presigned permite acesso temporário ao arquivo sem necessidade de autenticação adicional
- Ideal para compartilhar arquivos de forma segura com tempo de validade

---

### 7. Deletar Arquivo

Remove um arquivo do storage.

#### `DELETE /delete/{filename}`

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `filename` | String | Nome único do arquivo |

**Query Parameters:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `bucket` | String | Não | Nome do bucket (default: "files") |

**Resposta de Sucesso:** `200 OK`

```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

**Resposta de Erro:** `404 Not Found`

```json
{
  "detail": "File not found or deletion failed"
}
```

**Exemplo:**

```bash
curl -X DELETE "http://localhost:8080/delete/9f12a750ce2f89862e13d9d5648165bac80f6e3c42af38b0829226ab97b96f1d.pdf?bucket=regulations"
```

**⚠️ Atenção:**
- A deleção é permanente e irreversível
- Se múltiplas entidades referenciam o mesmo arquivo (via hash), todas perderão acesso

---

## Conceitos Importantes

### Deduplicação

O Storage Service utiliza hash SHA256 para identificar arquivos únicos. Quando um arquivo é enviado:

1. **Calcula o hash SHA256** do conteúdo
2. **Verifica se já existe** um arquivo com o mesmo hash
3. **Se existe:** Retorna informações do arquivo existente (`already_exists: true`)
4. **Se não existe:** Faz upload e armazena

**Vantagens:**
- Economia de espaço em disco
- Upload instantâneo de arquivos duplicados
- Garante integridade dos dados

**Exemplo:**

```bash
# Primeiro upload
curl -X POST http://localhost:8080/upload -F "file=@doc.pdf" -F "bucket=files"
# Resposta: "already_exists": false

# Segundo upload do MESMO arquivo
curl -X POST http://localhost:8080/upload -F "file=@doc.pdf" -F "bucket=files"
# Resposta: "already_exists": true (não faz upload novamente!)
```

---

### Buckets

Buckets são containers lógicos para organizar arquivos. Cada bucket:

- É criado automaticamente no primeiro upload
- Pode ter políticas de acesso independentes
- Funciona como uma "pasta" de alto nível

**Buckets Recomendados:**

| Bucket | Uso |
|--------|-----|
| `files` | Arquivos genéricos (default) |
| `regulations` | Regulamentos de modalidades |
| `images` | Fotos e imagens |
| `documents` | Documentos oficiais |
| `avatars` | Fotos de perfil |
| `logos` | Logos de cursos/equipas |

**Exemplo de Organização:**

```
MinIO
├── regulations/
│   ├── abc123...def.pdf
│   └── xyz789...ghi.pdf
├── images/
│   ├── 456def...789.jpg
│   └── 123abc...456.png
└── files/
    └── 999zzz...111.txt
```

---

### Metadados Customizados

Você pode armazenar informações adicionais com cada arquivo:

```bash
curl -X POST http://localhost:8080/upload \
  -F "file=@documento.pdf" \
  -F "bucket=regulations" \
  -F 'metadata={
    "uploaded_by": "admin_123",
    "category": "regulation",
    "modality_id": "uuid-modalidade",
    "season": "2024-2025",
    "version": "1.0"
  }'
```

**Metadados são úteis para:**
- Rastreabilidade (quem fez upload)
- Categorização
- Versionamento
- Filtros e buscas

---

### Acesso Público vs Privado

Por padrão, os buckets criados pelo Storage Service têm **acesso público de leitura** (desenvolvimento).

**URL Direta (Pública):**
```
http://localhost:9000/regulations/abc123...def.pdf
```

**URL Presigned (Privada/Temporária):**
```
http://localhost:9000/regulations/abc123...def.pdf?X-Amz-Algorithm=...
```

**Para produção:** Recomenda-se usar apenas URLs presigned para maior segurança.

---

## Integração com Django

### Cliente Python

Use o `StorageServiceClient` para integrar com suas aplicações Django:

```python
from storage_client import StorageServiceClient

# Inicializar
storage = StorageServiceClient()

# Upload
result = storage.upload_file(
    file_content=file.read(),
    filename=file.name,
    content_type=file.content_type,
    bucket="regulations",
    metadata={"user_id": str(request.user.id)}
)

# Download
content = storage.download_file(
    filename=result['filename'],
    bucket="regulations"
)

# Verificar existência
exists = storage.file_exists(
    file_hash=result['hash'],
    extension=".pdf",
    bucket="regulations"
)
```

### Exemplo Completo em Django View

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from storage_client import StorageServiceClient
from .models import Regulation

storage = StorageServiceClient()

class RegulationUploadView(APIView):
    def post(self, request):
        file = request.FILES['file']

        # Upload para storage
        result = storage.upload_file(
            file_content=file.read(),
            filename=file.name,
            content_type=file.content_type,
            bucket="regulations",
            metadata={
                "uploaded_by": str(request.user.id),
                "modality_id": request.data.get("modality_id")
            }
        )

        # Salvar no banco de dados
        regulation = Regulation.objects.create(
            title=request.data['title'],
            file_url=result['url'],
            file_hash=result['hash'],
            file_size=result['size'],
            file_name=result['original_filename'],
            content_type=result['content_type'],
            created_by=request.user
        )

        return Response({
            "id": regulation.id,
            "hash": result['hash'],
            "url": result['url'],
            "already_exists": result['already_exists']
        })
```

---

## Variáveis de Ambiente

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `MINIO_ENDPOINT` | Endpoint do MinIO | `minio:9000` |
| `MINIO_ROOT_USER` | Usuário do MinIO | `admin` |
| `MINIO_ROOT_PASSWORD` | Senha do MinIO | `adminadmin` |
| `MINIO_SECURE` | Usar HTTPS | `false` |
| `MINIO_PUBLIC_ENDPOINT` | Endpoint público para URLs | `localhost:9000` |
| `DEFAULT_BUCKET` | Bucket padrão | `files` |

---

## Códigos de Erro

### HTTP Status Codes

| Código | Descrição |
|--------|-----------|
| `200 OK` | Requisição bem-sucedida |
| `201 Created` | Recurso criado (não usado atualmente) |
| `400 Bad Request` | Dados inválidos na requisição |
| `404 Not Found` | Arquivo não encontrado |
| `500 Internal Server Error` | Erro interno do servidor |

### Formato de Erro

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Limites e Restrições

### Tamanho de Arquivo

- **Limite recomendado:** 10MB por arquivo
- **Limite técnico:** Configurável no MinIO (padrão 5GB)

### Taxa de Requisições

- **Não há limite** implementado atualmente
- Para produção, recomenda-se implementar rate limiting

### Tipos de Arquivo

- **Suportados:** Qualquer tipo de arquivo
- **Recomendados:** PDF, DOCX, JPG, PNG, TXT
- **Validação:** Feita pela aplicação cliente, não pelo Storage Service

---

## Monitoramento e Logs

### Health Check

Use o endpoint `/health` para monitoramento:

```bash
# Verificar status
curl http://localhost:8080/health

# Integração com Kubernetes
livenessProbe:
  httpGet:
    path: /health
    port: 8000
```

### Logs

O serviço registra logs estruturados:

```bash
# Ver logs em tempo real
docker-compose logs -f storage-service

# Logs de upload
INFO: Bucket 'regulations' created successfully
INFO: 172.18.0.1:32932 - "POST /upload HTTP/1.1" 200 OK

# Logs de erro
ERROR: Failed to upload file: Connection timeout
```

---

## Segurança

### Autenticação Interna

Para produção, implemente autenticação entre serviços:

- **Mutual TLS:** Certificados cliente/servidor
- **JWT Tokens:** Tokens de serviço com scopes limitados
- **API Keys:** Chaves específicas por serviço

### Boas Práticas

1. **Use URLs presigned** em produção
2. **Valide tipos de arquivo** no cliente
3. **Limite tamanho de upload** no gateway
4. **Implemente rate limiting** por IP/serviço
5. **Escaneie arquivos** por malware (integração externa)
6. **Use HTTPS** em produção (`MINIO_SECURE=true`)

---

## Performance

### Otimizações Implementadas

- ✅ Deduplicação automática (economiza espaço e tempo)
- ✅ Streaming de arquivos (baixo uso de memória)
- ✅ Buckets criados automaticamente
- ✅ Health checks rápidos (socket TCP)

### Recomendações

- **CDN:** Use CloudFront ou similar na frente do MinIO
- **Cache:** URLs presigned podem ser cacheadas
- **Compressão:** Comprima arquivos antes do upload (se apropriado)
- **Múltiplas instâncias:** MinIO suporta clustering

---

## Troubleshooting

### Arquivo não encontrado após upload

**Problema:** Upload retorna sucesso mas download falha

**Solução:**
1. Verifique os logs do MinIO
2. Confirme que o bucket foi criado
3. Verifique permissões do bucket

### Access Denied no navegador

**Problema:** URL retorna "Access Denied"

**Solução:**
1. Use URL presigned temporária
2. Configure bucket como público no MinIO Console
3. Verifique variável `MINIO_PUBLIC_ENDPOINT`

### Upload lento

**Problema:** Upload de arquivos grandes é muito lento

**Solução:**
1. Verifique rede entre serviços
2. Aumente timeout no cliente
3. Considere upload em chunks (não implementado)

### Health check falha

**Problema:** Container não fica healthy

**Solução:**
1. Verifique se MinIO está acessível
2. Confirme variáveis de ambiente
3. Verifique logs: `docker logs storage-service`

---

## Changelog

### v1.0.0 (2024-12-09)

- ✅ Upload de arquivos com deduplicação
- ✅ Download de arquivos
- ✅ Metadados customizados
- ✅ Multi-bucket support
- ✅ URLs presigned
- ✅ Health check endpoint
- ✅ Políticas públicas automáticas (desenvolvimento)

---

## Suporte

- **Repositório:** `src/microservices/storage-service/`
- **Documentação:** `STORAGE_SERVICE_API.md`
- **Cliente Python:** `src/shared/storage_client/`

---

**Gerado em:** 2024-12-09
**Versão:** 1.0.0
