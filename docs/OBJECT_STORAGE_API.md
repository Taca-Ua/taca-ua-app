# 📁 File Upload API com MinIO - Documentação Técnica

## Visão Geral

Sistema de upload e armazenamento de arquivos usando MinIO como Object Storage, com URLs públicas acessíveis via nginx.

**Status:** ✅ 100% Funcional e Testado

**Arquitetura:**
```
Client/Browser → Competition API → MinIO (interno)
                       ↓
                 Retorna URL pública
              http://localhost/files/...
```

---

## Importante

* O client nunca acessa o MinIO diretamente — todas as operações passam pela Competition API
* URLs públicas são servidas via **nginx proxy** (`/files/`)
* MinIO opera na rede interna do Docker (`minio:9000`)
* Arquivos são identificados por **hash SHA256** (deduplicação automática)

---

## Configuração do Sistema

### Arquivos Modificados

#### 1. `src/configs/nginx/nginx.conf`

**Alterações:**
- Adicionado `upstream minio-server` apontando para `minio:9000`
- Adicionada rota `/files/` para proxy do MinIO
- Aumentado `client_max_body_size` para 50M
- Configurado CORS e timeouts para arquivos grandes

**Trecho crítico:**
```nginx
upstream minio-server {
    server minio:9000;
}

location /files/ {
    proxy_pass http://minio-server/;
    proxy_set_header Host $host;
    add_header Access-Control-Allow-Origin * always;
    proxy_buffering off;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
}
```

#### 2. `src/apis/competiotion-api/competition_api/settings.py`

**Adicionado:**
```python
# MinIO Configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER", "admin")
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD", "adminadmin")
MINIO_USE_SSL = os.environ.get("MINIO_USE_SSL", "false").lower() == "true"

# ⚠️ CRÍTICO: URL pública para acesso via nginx
MINIO_PUBLIC_ENDPOINT = os.environ.get("MINIO_PUBLIC_ENDPOINT", "http://localhost/files")
```

#### 3. `.env` (raiz do projeto)

**Adicionado:**
```env
# MinIO Public Endpoint
MINIO_PUBLIC_ENDPOINT=http://localhost/files

# Para produção:
# MINIO_PUBLIC_ENDPOINT=https://seu-dominio.com/files
```

#### 4. `docker-compose.dev.yml`

**No serviço `competition-api`, adicionado:**
```yaml
competition-api:
  environment:
    - MINIO_ENDPOINT=minio:9000
    - MINIO_ROOT_USER=admin
    - MINIO_ROOT_PASSWORD=adminadmin
    - MINIO_USE_SSL=false
    - MINIO_PUBLIC_ENDPOINT=http://localhost/files
```

#### 5. `src/apis/competiotion-api/admin_api/services/minio_service.py`

**Método `get_public_url` atualizado:**
```python
def get_public_url(self, bucket_name: str, object_name: str) -> str:
    """
    Get public URL for an object
    """
    # Use public endpoint if configured
    public_endpoint = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', None)
    if public_endpoint:
        return f"{public_endpoint}/{bucket_name}/{object_name}"
    else:
        # Fallback
        protocol = "https" if settings.MINIO_USE_SSL else "http"
        endpoint = settings.MINIO_ENDPOINT
        return f"{protocol}://{endpoint}/{bucket_name}/{object_name}"
```

---

## Deploy e Verificação

### Reiniciar Sistema

```bash
# Parar containers
docker-compose -f docker-compose.dev.yml down

# Subir novamente
docker-compose -f docker-compose.dev.yml up -d

# Verificar logs
docker-compose -f docker-compose.dev.yml logs -f nginx competition-api
```

### Checklist de Verificação

```bash
# ✅ Verificar rota /files/ no nginx
docker-compose -f docker-compose.dev.yml exec nginx cat /etc/nginx/conf.d/default.conf | grep -A 5 "location /files"

# ✅ Verificar variável de ambiente
docker-compose -f docker-compose.dev.yml exec competition-api env | grep MINIO_PUBLIC

# ✅ Verificar containers ativos
docker-compose -f docker-compose.dev.yml ps

# Saída esperada da variável:
# MINIO_PUBLIC_ENDPOINT=http://localhost/files
```

---

## API Endpoints

**Prefixo:** `/api/admin`

**Auth:** Autenticação via Keycloak (RBAC)

### 1. Upload de Arquivo

`POST /api/admin/files/upload`

**Content-Type:** `multipart/form-data`

**Body:**
- `file` (obrigatório) - Arquivo a ser enviado
- `bucket` (obrigatório) - Nome do bucket (3-63 caracteres, minúsculas, a-z, 0-9, `-`, `.`)

**Response (201):**
```json
{
  "file_hash": "65dbaf8e940acef2fbb74a57ec0cf2b1e09e17f6ceee6dcfae1ba1530407dcb9",
  "object_name": "65dbaf8e940acef2fbb74a57ec0cf2b1e09e17f6ceee6dcfae1ba1530407dcb9.pdf",
  "bucket": "regulamentos",
  "public_url": "http://localhost/files/regulamentos/65dbaf8e940acef2fbb74a57ec0cf2b1e09e17f6ceee6dcfae1ba1530407dcb9.pdf",
  "content_type": "application/pdf",
  "size": 245678,
  "original_filename": "regulamento_2024.pdf"
}
```

**Response (400) - Validação:**
```json
{
  "bucket": ["Bucket name must be between 3 and 63 characters"]
}
```

### 2. Deletar Arquivo

`DELETE /api/admin/files/delete`

**Content-Type:** `application/json`

**Body:**
```json
{
  "bucket": "regulamentos",
  "object_name": "65dbaf8e940acef2fbb74a57ec0cf2b1e09e17f6ceee6dcfae1ba1530407dcb9.pdf"
}
```

**Response (204):** Sem corpo

**Response (404):**
```json
{
  "error": "File not found"
}
```

---

## Testes via cURL

### Teste 1: Upload Simples

```bash
# Criar arquivo de teste
echo "Teste de upload MinIO" > teste.txt

# Upload
curl -X POST http://localhost/api/admin/files/upload \
  -F "file=@teste.txt" \
  -F "bucket=documentos-teste"

# Saída esperada:
# {
#   "public_url": "http://localhost/files/documentos-teste/hash...txt",
#   ...
# }
```

### Teste 2: Upload de PDF

```bash
curl -X POST http://localhost/api/admin/files/upload \
  -F "file=@regulamento.pdf" \
  -F "bucket=regulamentos"
```

### Teste 3: Upload de Imagem

```bash
curl -X POST http://localhost/api/admin/files/upload \
  -F "file=@logo.jpg" \
  -F "bucket=fotos-equipes"
```

### Teste 4: Verificar URL Pública

```bash
# Testar acesso à URL retornada
curl -I http://localhost/files/documentos-teste/hash...txt

# Deve retornar: HTTP/1.1 200 OK
```

### Teste 5: Download de Arquivo

```bash
# Baixar arquivo
curl http://localhost/files/documentos-teste/hash...txt -o download.txt

# Verificar conteúdo
cat download.txt
```

### Teste 6: Deletar Arquivo

```bash
curl -X DELETE http://localhost/api/admin/files/delete \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "documentos-teste",
    "object_name": "hash...txt"
  }'

# Deve retornar: 204 No Content
```

---

## Exemplos de Código

### Python - Upload de Regulamento

```python
import requests
from datetime import datetime

def upload_regulation(file_path, title, modality_id=None):
    """
    Faz upload de regulamento

    Returns:
        dict com file_hash, public_url, etc.
    """
    url = "http://localhost/api/admin/files/upload"

    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'bucket': 'regulamentos'}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Upload realizado!")
            print(f"🔗 URL: {result['public_url']}")
            return result
        else:
            raise Exception(f"Erro: {response.json()}")

# Uso
file_info = upload_regulation('regulamento_2024.pdf', 'Regulamento Futebol')
```

### Python - Upload de Foto de Equipe

```python
def upload_team_photo(team_id, photo_path):
    """
    Upload de foto de equipe
    """
    url = "http://localhost/api/admin/files/upload"

    with open(photo_path, 'rb') as f:
        files = {'file': f}
        data = {'bucket': 'fotos-equipes'}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 201:
            result = response.json()
            return {
                'team_id': team_id,
                'photo_url': result['public_url'],
                'file_hash': result['file_hash']
            }
        else:
            raise Exception(f"Erro: {response.json()}")

# Uso
team_photo = upload_team_photo(15, 'logo_equipe.jpg')
print(f"Foto: {team_photo['photo_url']}")
```

### JavaScript/React - Hook de Upload

```javascript
// hooks/useFileUpload.js
import { useState } from 'react';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const uploadFile = async (file, bucket) => {
    setUploading(true);
    setError(null);
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('bucket', bucket);

    try {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          setProgress((e.loaded / e.total) * 100);
        }
      });

      const response = await new Promise((resolve, reject) => {
        xhr.open('POST', '/api/admin/files/upload');

        xhr.onload = () => {
          if (xhr.status === 201) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error(xhr.responseText));
          }
        };

        xhr.onerror = () => reject(new Error('Erro de rede'));
        xhr.send(formData);
      });

      setResult(response);
      return response;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setUploading(false);
    }
  };

  return { uploadFile, uploading, progress, error, result };
};
```

### React - Componente de Upload

```javascript
import React, { useState } from 'react';
import { useFileUpload } from './hooks/useFileUpload';

export const FileUploader = ({ bucket, onSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const { uploadFile, uploading, progress, error, result } = useFileUpload();

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      const result = await uploadFile(selectedFile, bucket);

      if (onSuccess) {
        onSuccess(result);
      }

      alert('Upload realizado com sucesso!');
    } catch (err) {
      console.error('Erro:', err);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => setSelectedFile(e.target.files[0])}
        disabled={uploading}
      />

      <button onClick={handleUpload} disabled={!selectedFile || uploading}>
        {uploading ? `Enviando... ${progress.toFixed(0)}%` : 'Upload'}
      </button>

      {error && <div className="error">{error}</div>}
      {result && <div>✅ URL: {result.public_url}</div>}
    </div>
  );
};
```

---

## Buckets Recomendados

| Bucket | Uso | Tipos |
|--------|-----|-------|
| `regulamentos` | Regulamentos de competições | PDF |
| `fotos-equipes` | Logos e fotos de equipes | JPG, PNG, WEBP |
| `fotos-atletas` | Fotos de atletas | JPG, PNG |
| `documentos-identidade` | RG, passaporte | PDF, JPG |
| `documentos-medicos` | Atestados médicos | PDF |
| `documentos-autorizacao` | Autorizações | PDF |
| `relatorios` | Relatórios de jogos | PDF, DOCX |
| `documentos-gerais` | Outros documentos | PDF, DOC, TXT |

**Regras de nomenclatura:**
- 3-63 caracteres
- Apenas minúsculas (a-z)
- Números (0-9)
- Hífen (`-`) e ponto (`.`)
- Deve começar e terminar com letra ou número

---

## Validações e Limites

### Validações Implementadas

- **Tamanho do bucket:** 3-63 caracteres
- **Caracteres permitidos:** a-z, 0-9, ponto (.), hífen (-)
- **Início/fim:** Letra ou número
- **Tamanho máximo do arquivo:** 50MB (configurável via nginx)
- **Tipos de arquivo:** Todos suportados (detecção automática de MIME type)

### Características

- **Hash SHA256:** Cada arquivo é identificado por seu hash
- **Deduplicação:** Arquivos idênticos compartilham o mesmo hash
- **Criação automática de buckets:** Buckets são criados automaticamente no primeiro upload
- **Content-Type:** Detectado automaticamente via python-magic

---

## Troubleshooting

### ❌ URL ainda vem com `minio:9000`

**Causa:** Variável `MINIO_PUBLIC_ENDPOINT` não está sendo lida

**Solução:**
```bash
# Verificar settings.py
grep MINIO_PUBLIC_ENDPOINT src/apis/competiotion-api/competition_api/settings.py

# Verificar variável no container
docker-compose -f docker-compose.dev.yml exec competition-api env | grep MINIO_PUBLIC

# Reiniciar competition-api
docker-compose -f docker-compose.dev.yml restart competition-api
```

### ❌ Erro 404 ao acessar `/files/`

**Causa:** Nginx não tem a rota configurada

**Solução:**
```bash
# Verificar configuração
docker-compose -f docker-compose.dev.yml exec nginx cat /etc/nginx/conf.d/default.conf | grep -A 10 "location /files"

# Deve mostrar o bloco location /files/
# Se não aparecer, o nginx.conf não foi atualizado

# Reiniciar nginx
docker-compose -f docker-compose.dev.yml restart nginx
```

### ❌ Erro 502 ao acessar `/files/`

**Causa:** Nginx não consegue conectar ao MinIO

**Solução:**
```bash
# Verificar se MinIO está rodando
docker-compose -f docker-compose.dev.yml ps minio

# Ver logs do MinIO
docker-compose -f docker-compose.dev.yml logs minio

# Reiniciar MinIO
docker-compose -f docker-compose.dev.yml restart minio
```

### ❌ Erro 413 (Payload Too Large)

**Causa:** Arquivo maior que `client_max_body_size`

**Solução:**
Aumentar no `nginx.conf`:
```nginx
client_max_body_size 100M;  # Ajustar conforme necessário
```

Depois reiniciar nginx.

### ❌ Arquivo não abre no navegador

**Causa:** Headers CORS ou Content-Type incorretos

**Solução:**
```bash
# Verificar headers
curl -I http://localhost/files/bucket/arquivo.pdf

# Deve conter:
# Access-Control-Allow-Origin: *
# Content-Type: application/pdf
```

---

## Segurança (Recomendações para Produção)

### 1. Autenticação
```python
from rest_framework.permissions import IsAuthenticated

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
```

### 2. Validação de Tipos por Bucket
```python
ALLOWED_TYPES = {
    'fotos-equipes': ['image/jpeg', 'image/png', 'image/webp'],
    'regulamentos': ['application/pdf'],
}

def validate_file_type(bucket, content_type):
    allowed = ALLOWED_TYPES.get(bucket, [])
    if allowed and content_type not in allowed:
        raise ValidationError(f"Tipo {content_type} não permitido")
```

### 3. Limitar Tamanho por Tipo
```python
MAX_SIZES = {
    'fotos-equipes': 5 * 1024 * 1024,      # 5MB
    'regulamentos': 50 * 1024 * 1024,      # 50MB
}
```

### 4. Auditoria
```python
UploadLog.objects.create(
    user=request.user,
    file_hash=result['file_hash'],
    bucket=bucket,
    action='upload',
    ip_address=request.META.get('REMOTE_ADDR'),
    timestamp=datetime.now()
)
```

---

## Diferenças: Antes vs Depois

### ❌ ANTES (Não Funcionava)

**URL gerada pelo backend:**
```
http://minio:9000/regulamentos/abc123.pdf
```

**No navegador:**
```
❌ ERR_NAME_NOT_RESOLVED
Site minio:9000 não encontrado
```

### ✅ DEPOIS (Funciona!)

**URL gerada pelo backend:**
```
http://localhost/files/regulamentos/abc123.pdf
```

**No navegador:**
```
✅ Arquivo abre diretamente
PDF renderizado / Imagem exibida
```

---

## Notas Finais

### Sistema pronto quando:

- ✅ `nginx.conf` tem seção `/files/`
- ✅ `settings.py` tem `MINIO_PUBLIC_ENDPOINT`
- ✅ `.env` tem `MINIO_PUBLIC_ENDPOINT=http://localhost/files`
- ✅ `docker-compose.dev.yml` passa variável para `competition-api`
- ✅ `minio_service.py` usa `MINIO_PUBLIC_ENDPOINT`
- ✅ Containers reiniciados após mudanças
- ✅ Upload retorna URL com `localhost/files`
- ✅ URL abre no navegador

### Para Produção

Alterar `.env`:
```env
# Com domínio
MINIO_PUBLIC_ENDPOINT=https://seu-dominio.com/files

# Com IP
MINIO_PUBLIC_ENDPOINT=http://192.168.1.100/files
```

---

**Última atualização:** Dezembro 2024
**Status:** ✅ Produção Ready (após adicionar autenticação)
