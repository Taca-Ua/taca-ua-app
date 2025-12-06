# API Alignment Changelog

**Data:** 6 de Dezembro de 2025
**Branch:** `frontend-geral`

## Resumo

Este documento detalha todas as alterações realizadas para alinhar as APIs Admin e Public, bem como as atualizações correspondentes nos frontends.

---

## 1. Estruturas de Dados Alinhadas

### 1.1 Regulamentos ✅

**Status:** Totalmente alinhados desde o início

**Estrutura (Admin & Public):**
```typescript
{
  id: number,
  title: string,
  description?: string,
  modality_id?: number,
  file_url: string,
  created_at: datetime
}
```

**Sem alterações necessárias.**

---

### 1.2 Modalidades ✅

**Alterações Realizadas:**

**Antes:**
```typescript
// Admin & Public (desalinhado)
{
  id: number,
  name: string,
  type?: string,
  description?: string  // ❌ Inconsistente
}
```

**Depois:**
```typescript
// Admin & Public (alinhado)
{
  id: number,
  name: string,
  type: 'coletiva' | 'individual' | 'mista',
  scoring_schema?: {
    win?: number,
    draw?: number,
    loss?: number
  }
}
```

**Mudanças:**
- ✅ Removido campo `description` (não existia na API)
- ✅ Adicionado campo `type` obrigatório
- ✅ Adicionado campo `scoring_schema` (JSON object)

**Ficheiros Alterados:**
- `src/apis/public-api/app/schemas/modalities.py`
- `src/apis/public-api/app/routes/modalities.py`
- `src/frontend/admin-panel/src/api/modalities.ts`
- `src/frontend/admin-panel/src/pages/geral/Modalidades.tsx`
- `src/frontend/admin-panel/src/pages/geral/ModalidadeDetail.tsx`
- `src/frontend/public-website/src/api/types.ts`

---

### 1.3 Épocas/Seasons ✅

**Alterações Realizadas:**

**Antes:**
```typescript
// Public API (desatualizado)
{
  id: string,        // ❌ Deveria ser number
  year: number,
  display_name: string,  // ❌ Não existe na API
  is_active: boolean     // ❌ Não existe na API
}
```

**Depois:**
```typescript
// Admin & Public (alinhado)
{
  id: number,
  year: number,
  status: 'draft' | 'active' | 'finished'
}
```

**Mudanças:**
- ✅ Removido campo `display_name`
- ✅ Removido campo `is_active`
- ✅ Adicionado campo `status` (enum)
- ✅ ID alterado de `string` para `number`

**Ficheiros Alterados:**
- `src/apis/public-api/app/schemas/seasons.py`
- `src/apis/public-api/app/routes/seasons.py`
- `src/apis/public-api/app/schemas/tournaments.py` (nested SeasonInfo)
- `src/apis/public-api/app/routes/tournaments.py` (mock data)
- `src/frontend/public-website/src/api/types.ts` (Season, TournamentPublicDetail, ModalityRanking, HistoricalWinner)
- `src/frontend/public-website/src/api/seasons.ts`
- `src/frontend/public-website/src/pages/classificacao/Geral.tsx`
- `src/frontend/public-website/src/pages/classificacao/Modalidade.tsx`
- `src/frontend/public-website/src/pages/classificacao/TorneioDetail.tsx`

**Gestão de Épocas:**
- ✅ Adicionada funcionalidade no Dashboard Admin para iniciar/terminar épocas
- ✅ Apenas uma época pode estar `active` de cada vez
- ✅ Épocas `finished` não podem ser reabertas

---

### 1.4 Torneios ⚠️

**Status:** Intencionalmente diferentes

**Admin API:**
```typescript
{
  id: number,
  modality_id: number,     // ← ID apenas
  season_id: number,       // ← ID apenas
  name: string,
  rules?: string,
  status: 'draft' | 'active' | 'finished',
  start_date?: datetime,
  teams: number[]          // ← Array de IDs
}
```

**Public API:**
```typescript
{
  id: number,
  name: string,
  modality: {              // ← Objeto aninhado
    id: number,
    name: string
  },
  season: {                // ← Objeto aninhado
    id: number,
    year: number
  },
  status: string,
  rules?: string,
  start_date?: string,
  team_count: number       // ← Contagem em vez de array
}
```

**Razão:** A Public API fornece objetos aninhados para melhor experiência do consumidor, reduzindo número de requests necessários.

**Ficheiros Alterados:**
- `src/apis/public-api/app/schemas/tournaments.py` (removido `display_name` de SeasonInfo)
- `src/apis/public-api/app/routes/tournaments.py` (atualizado mock data)

---

## 2. Correções de Tipos TypeScript

### 2.1 IDs: String → Number

**Problema:** Frontend usava `string` para IDs, mas API retorna `number`.

**Interfaces Corrigidas:**
```typescript
// Antes
Modality.id: string        → number
Season.id: string          → number (em objetos aninhados)
TournamentPublicDetail.id: string → number

// Depois - Todos alinhados com number
```

**Ficheiros Alterados:**
- `src/frontend/public-website/src/api/types.ts`
- `src/frontend/public-website/src/api/modalities.ts`
- `src/frontend/public-website/src/api/tournaments.ts`
- `src/frontend/public-website/src/api/rankings.ts`

### 2.2 Parâmetros de API

**Problema:** Funções esperavam `string`, mas recebiam `number`.

**Solução:** Aceitar `number | string` e converter internamente.

**Ficheiros Alterados:**
- `src/frontend/public-website/src/api/rankings.ts`
- `src/frontend/public-website/src/api/tournaments.ts`

---

## 3. Alterações no Frontend Admin

### 3.1 Modalidades

**Removido:**
- Campo `year` (modalidades não são específicas de época)
- Campo `description`
- Filtro por época na listagem

**Adicionado:**
- Campo `scoring_schema` como JSON object
- Validação JSON para scoring_schema

**Ficheiros:**
- `src/frontend/admin-panel/src/pages/geral/Modalidades.tsx`
- `src/frontend/admin-panel/src/pages/geral/ModalidadeDetail.tsx`

### 3.2 Dashboard - Gestão de Épocas

**Adicionado:**
- Seção de gestão de épocas no dashboard principal
- Botão "Iniciar Época" (com confirmação textual "INICIAR")
- Botão "Terminar Época" (com confirmação textual "FINALIZAR")
- Avisos visuais sobre ações irreversíveis
- Display da época atual

**Ficheiro:**
- `src/frontend/admin-panel/src/pages/geral/DashboardGeral.tsx`
- `src/frontend/admin-panel/src/api/seasons.ts`

---

## 4. Alterações no Frontend Public

### 4.1 Páginas de Classificação

**Alterações:**
- `s.is_active` → `s.status === 'active'`
- `{season.display_name}` → `Época {season.year}`

**Ficheiros:**
- `src/frontend/public-website/src/pages/classificacao/Geral.tsx`
- `src/frontend/public-website/src/pages/classificacao/Modalidade.tsx`
- `src/frontend/public-website/src/pages/classificacao/TorneioDetail.tsx`

### 4.2 API Helpers

**Atualizados para aceitar IDs numéricos:**
- `api.seasons.getActiveSeason()`
- `api.rankings.getGeneralRanking(seasonId)`
- `api.rankings.getModalityRanking(modalityId, seasonId)`
- `api.tournaments.getTournaments(params)`
- `api.tournaments.getTournamentDetail(tournamentId)`

---

## 5. Mock Data Atualizado

### 5.1 Public API

**Seasons:**
```python
[
  {"id": 1, "year": 2023, "status": "finished"},
  {"id": 2, "year": 2024, "status": "active"},
  {"id": 3, "year": 2025, "status": "draft"}
]
```

**Modalities:**
```python
[
  {"id": 1, "name": "Futebol", "type": "coletiva", "scoring_schema": {"win": 3, "draw": 1, "loss": 0}},
  {"id": 2, "name": "Futsal", "type": "coletiva", "scoring_schema": {"win": 3, "draw": 1, "loss": 0}},
  ...
]
```

**Tournaments:** Removido `display_name` de todos os objetos `season` aninhados.

---

## 6. Documentação Atualizada

**Ficheiros Modificados:**
- `docs/API_ENDPOINTS.md` - Adicionado changelog e exemplos atualizados
- `docs/DATABASE_MODELS.md` - Atualizada estrutura de modalidades e épocas

---

## 7. Verificação de Consistência

### Admin API ↔ Public API

| Endpoint | Admin | Public | Status |
|----------|-------|--------|--------|
| **Regulamentos** | `id, title, description, modality_id, file_url, created_at` | `id, title, description, modality_id, file_url, created_at` | ✅ Alinhado |
| **Modalidades** | `id, name, type, scoring_schema` | `id, name, type, scoring_schema` | ✅ Alinhado |
| **Épocas** | `id, year, status` | `id, year, status` | ✅ Alinhado |
| **Torneios** | IDs apenas | Objetos aninhados | ⚠️ Diferente (intencional) |

### Frontend Admin ↔ Admin API

| Feature | Status |
|---------|--------|
| Modalidades sem year/description | ✅ Correto |
| Scoring schema como JSON | ✅ Correto |
| Épocas com status enum | ✅ Correto |
| Gestão de épocas no dashboard | ✅ Implementado |

### Frontend Public ↔ Public API

| Feature | Status |
|---------|--------|
| Season.status em vez de is_active | ✅ Correto |
| IDs numéricos | ✅ Correto |
| Sem display_name | ✅ Correto |
| Modalities com scoring_schema | ✅ Correto |

---

## 8. Comandos Executados

```bash
# Restart services para aplicar mudanças
docker compose -f docker-compose.dev.yml restart public-api
docker compose -f docker-compose.dev.yml restart admin-panel
docker compose -f docker-compose.dev.yml restart public-website
```

---

## 9. Breaking Changes

### Para Consumidores da Public API

**⚠️ BREAKING CHANGES:**

1. **Seasons:**
   - Campo `display_name` removido → Use `year`
   - Campo `is_active` removido → Use `status === 'active'`
   - ID é `number`, não `string`

2. **Modalities:**
   - Campo `description` removido → Use `scoring_schema`
   - Campo `type` agora obrigatório
   - ID é `number`, não `string`

3. **Tournaments:**
   - IDs de objetos aninhados são `number`, não `string`

### Para Administradores

**⚠️ ATENÇÃO:**

1. **Modalidades:** Não tentam associar época - modalidades são independentes
2. **Épocas:** Apenas UMA época pode estar ativa. Iniciar nova época termina automaticamente a anterior
3. **Terminar Época:** Ação irreversível - época não pode ser reaberta


---

**Autor:** GitHub Copilot
**Revisão:** Pendente
