# Endpoints Internos dos Microserviços

Este documento detalha os endpoints REST internos de cada microserviço, bem como os eventos que cada um deve consumir do sistema de mensagens.

**Nota:** Estes endpoints são internos e não são expostos publicamente. A Competition API chama-os usando o DNS interno dos serviços (ex.: `http://matches-service:8000/...`, `http://modalities-service:8000/...`) ou o Read-Model Updater subscreve os eventos.

---

## 1. TOURNAMENTS-SERVICE

Responsável pela gestão de torneios, incluindo criação, atualização, associação de equipas e finalização.

### Endpoints REST Internos

#### 1.1 Criar Torneio
`POST http://tournaments-service:8000/tournaments`

**Body:**
- `modality_id` (obrigatório) - UUID da modalidade
- `name` (obrigatório) - Nome do torneio
- `season_id` (obrigatório) - UUID da época
- `rules` (opcional) - JSON com regras específicas
- `teams` (opcional) - Lista de UUIDs das equipas
- `start_date` (opcional) - Data de início (ISO 8601)
- `created_by` (obrigatório) - UUID do utilizador que criou

**Retorna:** `201 Created` com o objeto do torneio criado

---

#### 1.2 Atualizar Torneio
`PUT http://tournaments-service:8000/tournaments/{tournament_id}`

**Body:**
- `name` (opcional) - Nome do torneio
- `rules` (opcional) - JSON com regras
- `teams` (opcional) - Lista de UUIDs das equipas (substitui a lista anterior)
- `start_date` (opcional) - Data de início
- `updated_by` (obrigatório) - UUID do utilizador

**Restrições:**
- Não permite atualização se o torneio estiver finalizado (`status = 'finished'`)

**Retorna:** `200 OK` com o objeto atualizado

---

#### 1.3 Adicionar Equipas ao Torneio
`POST http://tournaments-service:8000/tournaments/{tournament_id}/teams`

**Body:**
- `team_ids` (obrigatório) - Lista de UUIDs das equipas a adicionar

**Restrições:**
- Não permite adicionar se o torneio estiver finalizado

**Retorna:** `200 OK`

---

#### 1.4 Remover Equipas do Torneio
`DELETE http://tournaments-service:8000/tournaments/{tournament_id}/teams`

**Body:**
- `team_ids` (obrigatório) - Lista de UUIDs das equipas a remover

**Restrições:**
- Não permite remover se o torneio estiver finalizado

**Retorna:** `204 No Content`

---

#### 1.5 Finalizar Torneio
`POST http://tournaments-service:8000/tournaments/{tournament_id}/finish`

**Body:**
- `finished_by` (obrigatório) - UUID do utilizador

**Ações:**
- Marca o torneio como `status = 'finished'`
- Bloqueia futuras edições
- **Publica evento:** `TournamentFinished`

**Retorna:** `200 OK`

---

#### 1.6 Obter Torneio
`GET http://tournaments-service:8000/tournaments/{tournament_id}`

**Retorna:** `200 OK` com detalhes do torneio

---

#### 1.7 Listar Torneios
`GET http://tournaments-service:8000/tournaments`

**Query Params (todos opcionais):**
- `modality_id` - Filtrar por modalidade
- `season_id` - Filtrar por época
- `status` - Filtrar por status (`draft`, `active`, `finished`)
- `limit` - Limite de resultados (default: 50)
- `offset` - Offset para paginação (default: 0)

**Retorna:** `200 OK` com lista de torneios

---

#### 1.8 Remover Torneio
`DELETE http://tournaments-service:8000/tournaments/{tournament_id}`

**Restrições:**
- Apenas permite remoção se `status = 'draft'`
- Não permite se houver jogos associados

**Retorna:** `204 No Content`

---

### Eventos que o Tournaments-Service Consome

#### `ModalityDeleted`
**Payload:**
- `modality_id` (UUID)

**Ação:**
- Marca todos os torneios dessa modalidade como inválidos ou cancela-os

---

#### `SeasonFinished`
**Payload:**
- `season_id` (UUID)

**Ação:**
- Finaliza automaticamente todos os torneios em aberto dessa época

---

### Eventos que o Tournaments-Service Publica

#### `TournamentCreated`
**Payload:**
- `tournament_id` (UUID)
- `modality_id` (UUID)
- `season_id` (UUID)
- `name` (string)
- `created_at` (timestamp)

---

#### `TournamentUpdated`
**Payload:**
- `tournament_id` (UUID)
- `changes` (objeto com campos alterados)
- `updated_at` (timestamp)

---

#### `TournamentFinished`
**Payload:**
- `tournament_id` (UUID)
- `modality_id` (UUID)
- `season_id` (UUID)
- `finished_at` (timestamp)

**Consumidores:**
- **ranking-service** - Recalcula pontuações finais

---

#### `TournamentDeleted`
**Payload:**
- `tournament_id` (UUID)
- `deleted_at` (timestamp)

---

## 2. MODALITIES-SERVICE

Responsável pela gestão de modalidades e equipas associadas aos cursos.

### Endpoints REST Internos

#### 2.1 Criar Modalidade
`POST http://modalities-service:8000/modalities`

**Body:**
- `name` (obrigatório) - Nome da modalidade
- `type` (obrigatório) - Tipo: `"coletiva"`, `"individual"`, `"mista"`
- `scoring_schema` (opcional) - JSON com esquema de pontuação
- `created_by` (obrigatório) - UUID do utilizador

**Retorna:** `201 Created` com o objeto da modalidade

---

#### 2.2 Atualizar Modalidade
`PUT http://modalities-service:8000/modalities/{modality_id}`

**Body:**
- `name` (opcional)
- `type` (opcional)
- `scoring_schema` (opcional)
- `updated_by` (obrigatório)

**Retorna:** `200 OK`

---

#### 2.3 Remover Modalidade
`DELETE http://modalities-service:8000/modalities/{modality_id}`

**Restrições:**
- Não permite remoção se houver torneios ou equipas associadas

**Ações:**
- **Publica evento:** `ModalityDeleted`

**Retorna:** `204 No Content`

---

#### 2.4 Obter Modalidade
`GET http://modalities-service:8000/modalities/{modality_id}`

**Retorna:** `200 OK`

---

#### 2.5 Listar Modalidades
`GET http://modalities-service:8000/modalities`

**Query Params (todos opcionais):**
- `type` - Filtrar por tipo
- `limit`, `offset`

**Retorna:** `200 OK` com lista de modalidades

---

#### 2.6 Criar Equipa
`POST http://modalities-service:8000/teams`

**Body:**
- `modality_id` (obrigatório) - UUID da modalidade
- `course_id` (obrigatório) - UUID do curso
- `name` (opcional) - Nome da equipa (se não fornecido, gera automaticamente)
- `players` (opcional) - Lista de UUIDs de estudantes
- `created_by` (obrigatório) - UUID do admin de núcleo

**Validações:**
- Verifica se o tipo da modalidade permite equipa (coletiva/mista)
- Verifica se os jogadores pertencem ao mesmo curso

**Retorna:** `201 Created` com o objeto da equipa

---

#### 2.7 Atualizar Equipa
`PUT http://modalities-service:8000/teams/{team_id}`

**Body:**
- `name` (opcional)
- `players_add` (opcional) - Lista de UUIDs a adicionar
- `players_remove` (opcional) - Lista de UUIDs a remover
- `updated_by` (obrigatório)

**Restrições:**
- Não permite modificação se a equipa estiver em torneio ativo

**Retorna:** `200 OK`

---

#### 2.8 Remover Equipa
`DELETE http://modalities-service:8000/teams/{team_id}`

**Restrições:**
- Não permite remoção se estiver em torneio ativo

**Retorna:** `204 No Content`

---

#### 2.9 Obter Equipa
`GET http://modalities-service:8000/teams/{team_id}`

**Retorna:** `200 OK`

---

#### 2.10 Listar Equipas
`GET http://modalities-service:8000/teams`

**Query Params (todos opcionais):**
- `modality_id` - Filtrar por modalidade
- `course_id` - Filtrar por curso
- `tournament_id` - Filtrar por torneio
- `limit`, `offset`

**Retorna:** `200 OK` com lista de equipas

---

#### 2.11 Criar Estudante
`POST http://modalities-service:8000/students`

**Body:**
- `course_id` (obrigatório) - UUID do curso
- `full_name` (obrigatório)
- `student_number` (obrigatório) - Único
- `email` (opcional)
- `is_member` (opcional) - Boolean, default: `false`
- `created_by` (obrigatório)

**Retorna:** `201 Created`

---

#### 2.12 Atualizar Estudante
`PUT http://modalities-service:8000/students/{student_id}`

**Body:**
- `full_name` (opcional)
- `email` (opcional)
- `is_member` (opcional)
- `updated_by` (obrigatório)

**Retorna:** `200 OK`

---

#### 2.13 Obter Estudante
`GET http://modalities-service:8000/students/{student_id}`

**Retorna:** `200 OK`

---

#### 2.14 Listar Estudantes
`GET http://modalities-service:8000/students`

**Query Params (todos opcionais):**
- `course_id` - Filtrar por curso (obrigatório na prática)
- `is_member` - Filtrar por status de membro
- `search` - Busca por nome ou número
- `limit`, `offset`

**Retorna:** `200 OK` com lista de estudantes

---

### Eventos que o Modalities-Service Consome

#### `CourseDeleted`
**Payload:**
- `course_id` (UUID)

**Ação:**
- Remove todas as equipas e estudantes desse curso
- Publica eventos de remoção

---

### Eventos que o Modalities-Service Publica

#### `ModalityCreated`
**Payload:**
- `modality_id` (UUID)
- `name` (string)
- `type` (string)
- `created_at` (timestamp)

---

#### `ModalityUpdated`
**Payload:**
- `modality_id` (UUID)
- `changes` (objeto)
- `updated_at` (timestamp)

---

#### `ModalityDeleted`
**Payload:**
- `modality_id` (UUID)
- `deleted_at` (timestamp)

---

#### `TeamCreated`
**Payload:**
- `team_id` (UUID)
- `modality_id` (UUID)
- `course_id` (UUID)
- `name` (string)
- `players` (lista de UUIDs)
- `created_at` (timestamp)

---

#### `TeamUpdated`
**Payload:**
- `team_id` (UUID)
- `changes` (objeto)
- `updated_at` (timestamp)

---

#### `TeamDeleted`
**Payload:**
- `team_id` (UUID)
- `deleted_at` (timestamp)

---

#### `StudentCreated`
**Payload:**
- `student_id` (UUID)
- `course_id` (UUID)
- `full_name` (string)
- `student_number` (string)
- `created_at` (timestamp)

---

## 3. MATCHES-SERVICE

Responsável pela gestão de jogos, resultados, escalões e comentários.

### Endpoints REST Internos

#### 3.1 Criar Jogo
`POST http://matches-service:8000/matches`

**Body:**
- `tournament_id` (obrigatório) - UUID do torneio
- `team_home_id` (obrigatório) - UUID da equipa casa
- `team_away_id` (obrigatório) - UUID da equipa visitante
- `location` (obrigatório) - Local do jogo
- `start_time` (obrigatório) - Data/hora do jogo (ISO 8601)
- `created_by` (obrigatório)

**Validações:**
- Verifica se as equipas pertencem ao torneio
- Verifica se não há conflito de horários para as equipas

**Retorna:** `201 Created` com o objeto do jogo

---

#### 3.2 Atualizar Jogo
`PUT http://matches-service:8000/matches/{match_id}`

**Body:**
- `location` (opcional)
- `start_time` (opcional)
- `team_home_id` (opcional)
- `team_away_id` (opcional)
- `updated_by` (obrigatório)

**Restrições:**
- Não permite alteração se o jogo já foi finalizado (`status = 'finished'`)

**Retorna:** `200 OK`

---

#### 3.3 Registar Resultado
`POST http://matches-service:8000/matches/{match_id}/result`

**Body:**
- `home_score` (obrigatório) - Integer ≥ 0
- `away_score` (obrigatório) - Integer ≥ 0
- `registered_by` (obrigatório)
- `additional_details` (opcional) - JSON com detalhes extra (golos, cartões, etc.)

**Ações:**
- Marca o jogo como `status = 'finished'`
- **Publica evento:** `MatchFinished`

**Retorna:** `200 OK`

---

#### 3.4 Atribuir Escalão (Lineup)
`POST http://matches-service:8000/matches/{match_id}/lineup`

**Body:**
- `team_id` (obrigatório) - UUID da equipa (casa ou visitante)
- `players` (obrigatório) - Lista de objetos:
  - `player_id` (UUID) - obrigatório
  - `jersey_number` (integer) - obrigatório
  - `is_starter` (boolean) - opcional, default: `true`

**Validações:**
- Verifica se os jogadores pertencem à equipa
- Verifica se o jogo ainda não foi finalizado

**Retorna:** `200 OK`

---

#### 3.5 Adicionar Comentário
`POST http://matches-service:8000/matches/{match_id}/comments`

**Body:**
- `message` (obrigatório) - Texto do comentário
- `author_id` (obrigatório) - UUID do utilizador
- `created_at` (opcional) - Timestamp (default: now)

**Retorna:** `201 Created`

---

#### 3.6 Obter Jogo
`GET http://matches-service:8000/matches/{match_id}`

**Retorna:** `200 OK` com detalhes completos do jogo (incluindo escalões e comentários)

---

#### 3.7 Listar Jogos
`GET http://matches-service:8000/matches`

**Query Params (todos opcionais):**
- `tournament_id` - Filtrar por torneio
- `modality_id` - Filtrar por modalidade
- `team_id` - Filtrar por equipa (casa ou visitante)
- `course_id` - Filtrar por curso (jogos envolvendo equipas do curso)
- `date` - Filtrar por data específica (ISO 8601)
- `date_from` - Filtrar a partir de data
- `date_to` - Filtrar até data
- `status` - Filtrar por status (`scheduled`, `in_progress`, `finished`, `cancelled`)
- `limit`, `offset`

**Retorna:** `200 OK` com lista de jogos

---

#### 3.8 Gerar Ficha de Jogo (PDF)
`GET http://matches-service:8000/matches/{match_id}/sheet`

**Query Params (todos opcionais):**
- `format` - Formato do documento (`pdf`, `json`), default: `pdf`

**Retorna:**
- `200 OK` com stream do PDF ou JSON com dados da ficha

---

#### 3.9 Remover Jogo
`DELETE http://matches-service:8000/matches/{match_id}`

**Restrições:**
- Não permite remoção se o jogo já foi finalizado

**Retorna:** `204 No Content`

---

### Eventos que o Matches-Service Consome

#### `TournamentFinished`
**Payload:**
- `tournament_id` (UUID)

**Ação:**
- Finaliza automaticamente todos os jogos pendentes do torneio
- Marca como cancelados se não tiverem resultado

---

#### `TeamDeleted`
**Payload:**
- `team_id` (UUID)

**Ação:**
- Cancela todos os jogos futuros dessa equipa
- Marca como inválidos

---

### Eventos que o Matches-Service Publica

#### `MatchCreated`
**Payload:**
- `match_id` (UUID)
- `tournament_id` (UUID)
- `team_home_id` (UUID)
- `team_away_id` (UUID)
- `start_time` (timestamp)
- `created_at` (timestamp)

---

#### `MatchUpdated`
**Payload:**
- `match_id` (UUID)
- `changes` (objeto)
- `updated_at` (timestamp)

---

#### `MatchFinished`
**Payload:**
- `match_id` (UUID)
- `tournament_id` (UUID)
- `team_home_id` (UUID)
- `team_away_id` (UUID)
- `home_score` (integer)
- `away_score` (integer)
- `finished_at` (timestamp)

**Consumidores:**
- **ranking-service** - Atualiza pontuações

---

#### `MatchCancelled`
**Payload:**
- `match_id` (UUID)
- `reason` (string)
- `cancelled_at` (timestamp)

---

## 4. RANKING-SERVICE

Responsável pelo cálculo e manutenção de classificações (geral, por modalidade, por curso).

### Endpoints REST Internos

#### 4.1 Recalcular Classificação de Modalidade
`POST http://ranking-service:8000/rankings/modality/{modality_id}/recalculate`

**Body:**
- `season_id` (opcional) - Se não fornecido, usa a época ativa
- `force` (opcional) - Boolean, força recálculo mesmo se atualizado

**Ações:**
- Busca todos os jogos finalizados da modalidade
- Aplica o `scoring_schema` da modalidade
- Atualiza tabela de classificação

**Retorna:** `200 OK`

---

#### 4.2 Recalcular Classificação de Curso
`POST http://ranking-service:8000/rankings/course/{course_id}/recalculate`

**Body:**
- `season_id` (opcional)
- `force` (opcional)

**Ações:**
- Agrega pontuações de todas as modalidades para o curso

**Retorna:** `200 OK`

---

#### 4.3 Recalcular Classificação Geral
`POST http://ranking-service:8000/rankings/general/recalculate`

**Body:**
- `season_id` (opcional)
- `force` (opcional)

**Ações:**
- Agrega todas as pontuações de todos os cursos

**Retorna:** `200 OK`

---

#### 4.4 Obter Classificação de Modalidade
`GET http://ranking-service:8000/rankings/modality/{modality_id}`

**Query Params (todos opcionais):**
- `season_id` - Filtrar por época

**Retorna:** `200 OK` com lista ordenada de equipas/cursos e pontuações

---

#### 4.5 Obter Classificação de Curso
`GET http://ranking-service:8000/rankings/course/{course_id}`

**Query Params (todos opcionais):**
- `season_id`

**Retorna:** `200 OK` com pontuação do curso em cada modalidade

---

#### 4.6 Obter Classificação Geral
`GET http://ranking-service:8000/rankings/general`

**Query Params (todos opcionais):**
- `season_id`

**Retorna:** `200 OK` com lista ordenada de cursos e pontuações totais

---

#### 4.7 Obter Histórico de Classificações
`GET http://ranking-service:8000/rankings/history`

**Query Params (todos opcionais):**
- `season_id` - Se não fornecido, retorna todas as épocas anteriores
- `course_id` - Filtrar por curso
- `limit`, `offset`

**Retorna:** `200 OK` com classificações de épocas anteriores

---

### Eventos que o Ranking-Service Consome

#### `MatchFinished`
**Payload:**
- `match_id` (UUID)
- `tournament_id` (UUID)
- `team_home_id` (UUID)
- `team_away_id` (UUID)
- `home_score` (integer)
- `away_score` (integer)
- `finished_at` (timestamp)

**Ação:**
- Atualiza pontuações incrementalmente
- Recalcula classificações afetadas (modalidade, curso, geral)

---

#### `TournamentFinished`
**Payload:**
- `tournament_id` (UUID)
- `modality_id` (UUID)
- `finished_at` (timestamp)

**Ação:**
- Força recálculo completo da modalidade
- Consolida pontuações finais

---

#### `SeasonFinished`
**Payload:**
- `season_id` (UUID)
- `finished_at` (timestamp)

**Ação:**
- Arquiva classificações finais da época
- Cria snapshot histórico

---

### Eventos que o Ranking-Service Publica

#### `RankingsUpdated`
**Payload:**
- `season_id` (UUID)
- `scope` (string) - `"modality"`, `"course"`, `"general"`
- `entity_id` (UUID) - ID da modalidade ou curso (se aplicável)
- `updated_at` (timestamp)

**Consumidores:**
- **read-model-updater** - Atualiza cache e read-model

---

## 5. READ-MODEL-UPDATER

Responsável por sincronizar eventos do write-model para a read-model store (Postgres + Redis).

**Nota:** Este serviço **não expõe endpoints REST**, apenas consome eventos e atualiza a base de dados de leitura.

### Eventos que o Read-Model-Updater Consome

Consome **TODOS** os eventos publicados pelos outros microserviços:

- `TournamentCreated`, `TournamentUpdated`, `TournamentFinished`, `TournamentDeleted`
- `ModalityCreated`, `ModalityUpdated`, `ModalityDeleted`
- `TeamCreated`, `TeamUpdated`, `TeamDeleted`
- `StudentCreated`, `StudentUpdated`
- `MatchCreated`, `MatchUpdated`, `MatchFinished`, `MatchCancelled`
- `RankingsUpdated`
- `CourseCreated`, `CourseUpdated`, `CourseDeleted` (da Competition API)
- `UserCreated`, `UserUpdated`, `UserDeleted` (da Competition API)
- `RegulationCreated`, `RegulationUpdated`, `RegulationDeleted` (da Competition API)
- `SeasonCreated`, `SeasonStarted`, `SeasonFinished` (da Competition API)

### Ações do Read-Model-Updater

Para cada evento:
1. **Valida** o evento
2. **Atualiza** as tabelas de leitura no Postgres
3. **Invalida cache** no Redis (se aplicável)
4. **Popula cache** com dados atualizados (para queries frequentes)

### Estratégias de Cache

- **Rankings gerais:** Cache de 5 minutos
- **Jogos do dia:** Cache de 1 minuto
- **Detalhes de torneios:** Cache de 10 minutos
- **Invalidação:** Ao receber evento relacionado

---

## Observações Finais

### Autenticação Interna

- Todos os endpoints internos devem usar **mutual TLS** ou **tokens JWT internos** para autenticação entre serviços.
- Não são expostos publicamente (apenas via rede interna/service mesh).

### Validações Comuns

Todos os serviços devem validar:
- UUIDs válidos
- Existência de entidades referenciadas
- Permissões de modificação (baseadas em `created_by` / `updated_by`)
- Restrições de negócio (ex: não editar entidades finalizadas)

### Sistema de Mensagens

- **Broker:** RabbitMQ ou Kafka (a definir)
- **Padrão:** Event-driven architecture com eventos imutáveis
- **Formato:** JSON com schema versionado
- **Garantias:** At-least-once delivery com idempotência nos consumidores

### Tratamento de Erros

Todos os endpoints devem retornar:
- `400 Bad Request` - Dados inválidos
- `404 Not Found` - Entidade não encontrada
- `409 Conflict` - Violação de restrição de negócio
- `422 Unprocessable Entity` - Validação de negócio falhou
- `500 Internal Server Error` - Erro do servidor

**Formato de erro:**
```json
{
  "error": {
    "code": "TOURNAMENT_ALREADY_FINISHED",
    "message": "Cannot update a finished tournament",
    "details": {
      "tournament_id": "uuid-here"
    }
  }
}
```

---

**Gerado em:** 2025-12-01
**Versão:** 1.0
