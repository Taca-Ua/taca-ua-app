# Database Models and Migrations

Este documento descreve a estrutura de base de dados do projeto Taca UA, implementada com SQLAlchemy e Alembic.

## Arquitetura

O sistema utiliza uma **única base de dados PostgreSQL** com **múltiplos schemas** para separação lógica entre microserviços:

### Schemas Privados (Write)
Cada microserviço escreve apenas no seu próprio schema:

- **`matches`** - Matches Service (jogos e resultados)
- **`tournaments`** - Tournaments Service (torneios, fases, jornadas)
- **`modalities`** - Modalities Service (modalidades e regras)
- **`ranking`** - Ranking Service (classificações)

### Schema Público (Read-Only)
- **`public_read`** - Read Model (projeções para leitura pela Public API)

## Estrutura de Tabelas

### 🎯 Matches Service (`matches` schema)

#### `matches.game`
Representa um jogo/partida:
- `id` (uuid) - ID do jogo
- `tournament_id` (uuid) - ID do torneio (FK indireta)
- `modality_id` (uuid) - ID da modalidade (FK indireta)
- `team_a_id` (uuid) - ID da equipa A
- `team_b_id` (uuid) - ID da equipa B
- `scheduled_at` (timestamp) - Data/hora agendada
- `location` (text) - Local do jogo
- `state` (enum) - Estado: `scheduled`, `finished`, `canceled`
- `created_at`, `updated_at` (timestamp)

#### `matches.result`
Armazena o resultado de um jogo (separado para auditoria):
- `id` (uuid)
- `game_id` (uuid) - FK para `matches.game`
- `team_a_score` (int)
- `team_b_score` (int)
- `submitted_by` (uuid) - Quem submeteu
- `submitted_at` (timestamp)

---

### 🏆 Tournaments Service (`tournaments` schema)

#### `tournaments.tournament`
- `id` (uuid)
- `modality_id` (uuid)
- `name` (text)
- `type` (enum) - `round_robin`, `elimination`, `groups`
- `season` (int)
- `created_at` (timestamp)

#### `tournaments.stage`
Fases de um torneio (ex: grupos, playoffs):
- `id` (uuid)
- `tournament_id` (uuid) - FK para `tournaments.tournament`
- `name` (text)
- `order` (int)

#### `tournaments.journey`
Jornadas dentro de uma fase:
- `id` (uuid)
- `stage_id` (uuid) - FK para `tournaments.stage`
- `number` (int)

---

### 🏅 Modalities Service (`modalities` schema)

#### `modalities.modality`
- `id` (uuid)
- `name` (text) - Nome da modalidade
- `description` (text)

#### `modalities.rule`
Regras de pontuação por modalidade:
- `id` (uuid)
- `modality_id` (uuid) - FK para `modalities.modality`
- `points_for_win` (int) - Pontos por vitória
- `points_for_draw` (int) - Pontos por empate
- `points_for_loss` (int) - Pontos por derrota
- `scoring_formula` (jsonb) - Fórmula customizada

---

### 📊 Ranking Service (`ranking` schema)

#### `ranking.team_ranking`
Classificação de equipas (recalculada por eventos):
- `id` (uuid)
- `tournament_id` (uuid)
- `team_id` (uuid)
- `wins`, `draws`, `losses` (int)
- `goals_for`, `goals_against` (int)
- `points` (int)
- `last_updated` (timestamp)

---

### 🌍 Public Read Model (`public_read` schema)

Views de leitura para a Public API (geridas pelo Read Model Updater):

#### `public_read.games_view`
- `game_id` (uuid)
- `tournament_name`, `modality_name` (text)
- `team_a_name`, `team_b_name` (text)
- `score` (text) - ex: "1-0"
- `scheduled_at` (timestamp)
- `state` (text)

#### `public_read.tournament_view`
- `tournament_id` (uuid)
- `name`, `modality` (text)
- `stage_count`, `total_matches` (int)

#### `public_read.ranking_view`
- `tournament_id` (uuid)
- `team` (text)
- `points`, `position` (int)

---

## Configuração do Alembic

Cada microserviço tem a sua própria pasta de migrations, mas todos apontam para a mesma base de dados:

```
matches-service/
  alembic.ini
  alembic/
    env.py
    versions/

tournaments-service/
  alembic.ini
  alembic/
    versions/

modalities-service/
  alembic.ini
  alembic/
    versions/

ranking-service/
  alembic.ini
  alembic/
    versions/

read-model-updater/
  alembic.ini
  alembic/
    versions/

public-api/
  alembic.ini
  alembic/
    versions/
```

### Configuração de Ambiente

Todos os serviços leem a URL da base de dados da variável de ambiente:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/tacaua
```

Ou edite no ficheiro `.env` na raiz do projeto.

---

## Como Usar

### 1. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Criar uma migration

Para cada serviço, navegue até à sua pasta e crie a migration:

```powershell
# Exemplo: Matches Service
cd src\microservices\matches-service
alembic revision --autogenerate -m "Create matches tables"

# Exemplo: Tournaments Service
cd src\microservices\tournaments-service
alembic revision --autogenerate -m "Create tournaments tables"
```

### 3. Aplicar as migrations

```powershell
# Para cada serviço
cd src\microservices\matches-service
alembic upgrade head

cd src\microservices\tournaments-service
alembic upgrade head

cd src\microservices\modalities-service
alembic upgrade head

cd src\microservices\ranking-service
alembic upgrade head

cd src\apis\public-api
alembic upgrade head
```

### 4. Verificar o estado das migrations

```powershell
alembic current
alembic history
```

### 5. Reverter uma migration

```powershell
alembic downgrade -1  # Volta uma versão
alembic downgrade <revision_id>  # Volta para uma revisão específica
```

---

## Importante

### ⚠️ Foreign Keys Indiretas

As Foreign Keys entre serviços **NÃO são enforced no banco de dados** para evitar coupling. Exemplo:
- `matches.game.tournament_id` não tem FK real para `tournaments.tournament.id`
- A integridade referencial é gerida pela lógica de aplicação

### ✅ Foreign Keys Internas

Foreign Keys **dentro do mesmo schema** são enforced:
- `matches.result.game_id` → `matches.game.id` ✅
- `tournaments.stage.tournament_id` → `tournaments.tournament.id` ✅

### 🔒 Read Model Updater

O **Read Model Updater** é o único serviço que:
1. Lê de todos os schemas privados (`matches`, `tournaments`, `modalities`, `ranking`)
2. Escreve no schema `public_read`

A **Public API** apenas **lê** do schema `public_read`.

---

## Dependências

Certifique-se de que estas dependências estão instaladas em cada serviço:

```txt
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.0  # ou psycopg[binary]
```

---

## Scripts Úteis

### Criar todas as migrations de uma vez

```powershell
# Script para criar migrations em todos os serviços
$services = @(
    "src\microservices\matches-service",
    "src\microservices\tournaments-service",
    "src\microservices\modalities-service",
    "src\microservices\ranking-service",
    "src\apis\public-api"
)

foreach ($service in $services) {
    Write-Host "Creating migration for $service"
    Push-Location $service
    alembic revision --autogenerate -m "Initial schema"
    Pop-Location
}
```

### Aplicar todas as migrations

```powershell
# Script para aplicar migrations em todos os serviços
$services = @(
    "src\microservices\matches-service",
    "src\microservices\tournaments-service",
    "src\microservices\modalities-service",
    "src\microservices\ranking-service",
    "src\apis\public-api"
)

foreach ($service in $services) {
    Write-Host "Upgrading $service"
    Push-Location $service
    alembic upgrade head
    Pop-Location
}
```

---

## Estrutura Final no PostgreSQL

Após todas as migrations, a base de dados terá:

```sql
-- Schemas
CREATE SCHEMA matches;
CREATE SCHEMA tournaments;
CREATE SCHEMA modalities;
CREATE SCHEMA ranking;
CREATE SCHEMA public_read;

-- Version tables (uma por schema)
-- matches.alembic_version
-- tournaments.alembic_version
-- modalities.alembic_version
-- ranking.alembic_version
-- public_read.alembic_version

-- Tabelas conforme descrito acima em cada schema
```

---

## Próximos Passos

1. ✅ Modelos criados
2. ✅ Alembic configurado
3. ⏳ Criar migrations: `alembic revision --autogenerate -m "Initial schema"`
4. ⏳ Aplicar migrations: `alembic upgrade head`
5. ⏳ Implementar lógica de negócio nos microserviços
6. ⏳ Implementar Read Model Updater para popular `public_read`
7. ⏳ Implementar Public API para ler de `public_read`
