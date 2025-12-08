# Importante

* Incluo apenas endpoints REST finais — **não incluo endpoints internos dos microservices**, que não são expostos externamente.
* Para cada endpoint coloco:

  * **Método**
  * **Path**
  * **Query params opcionais**
  * **Body (com campos obrigatórios e opcionais)**

## Atualizações Recentes (Dezembro 2025)

**Alinhamento de APIs (6 Dezembro 2025):**
- ✅ **Regulamentos**: Admin e Public APIs totalmente alinhados (`id`, `title`, `description`, `modality_id`, `file_url`, `created_at`)
- ✅ **Modalidades**: Removido campo `description`, adicionado `scoring_schema` (tipo: dict/JSON) em ambas APIs
- ✅ **Épocas/Seasons**: Removidos campos `display_name` e `is_active`, agora usa `status` enum (`draft`, `active`, `finished`)
- ✅ **Torneios**: Public API usa objetos aninhados (modality, season) para melhor experiência do consumidor; Admin API usa IDs
- ✅ **Frontend Public**: Todos os tipos TypeScript atualizados (IDs number, status enum, sem display_name)
- ✅ **Frontend Admin**: Modalidades simplificadas (sem year/description), scoring_schema como JSON object

**Gestão de Estudantes (RF4):**
- ✅ Adicionado campo `member_type` para distinguir estudantes ('student') de equipa técnica ('technical_staff')
- ✅ Adicionado endpoint `DELETE /api/admin/students/{student_id}`
- ✅ Campo `member_type` disponível em CREATE, UPDATE e GET responses

**Gestão de Equipas (RF4):**
- ✅ Adicionado parâmetro `?all=true` em `GET /api/admin/teams` para obter equipas de todos os cursos

**Gestão de Jogos (RF7):**
- ✅ Simplificado formato do endpoint `POST /api/admin/matches/{match_id}/lineup`
- ✅ Agora aceita array simples de player IDs ao invés de objetos complexos

**Frontend:**
- ✅ Removidas dependências de variáveis de ambiente (`.env`)
- ✅ URLs hardcoded: `/api/admin` (admin panel) e `/api/public` (public website)

# 1. COMPETITION API (ADMIN API)

Usada por:

* **Administrador Geral**
* **Administrador de Núcleo**
* Com autenticação **Keycloak** (RBAC).

A Competition API apenas **recebe comandos** (write-model), que depois sao processados internamente por vários micro-serviços.

**Prefixo base**: `/api/admin`

⚠️ **Nota sobre autenticação**: Apenas a Competition API (Django) valida tokens Keycloak. Os microservices internos e a Public API **não** usam Keycloak — comunicam internamente via RabbitMQ ou são públicos.

---

## 1. Gestão de Utilizadores e Autenticação (RF1)

**Auth:** Apenas Admin Geral
**Notes:** Integração com Keycloak — restabeleces os utilizadores via API própria, mas esta API regista-os no sistema e faz binding com curso/roles.

### **1.1 Listar administradores de núcleo**

`GET /api/admin/users/nucleo`

* Optional: `course_id`

### **1.2 Criar administrador de núcleo**

`POST /api/admin/users/nucleo`
Body:

* `username` (obrigatório)
* `email` (obrigatório)
* `course_id` (obrigatório)
* `full_name` (opcional)

### **1.3 Atualizar administrador de núcleo**

`PUT /api/admin/users/nucleo/{user_id}`
Body:

* `course_id` (opcional)
* `full_name` (opcional)

### **1.4 Remover administrador de núcleo**

`DELETE /api/admin/users/nucleo/{user_id}`

---

## 2. Gestão de Cursos (RF2)

**Auth:** Admin Geral

### **2.1 Listar cursos**

`GET /api/admin/courses`

### **2.2 Criar curso**

`POST /api/admin/courses`
Body:

* `name` (obrigatório)
* `short_code` (obrigatório)
* `color` (opcional)

### **2.3 Atualizar curso**

`PUT /api/admin/courses/{course_id}`
Body:

* `name` (opcional)
* `short_code` (opcional)
* `color` (opcional)

### **2.4 Remover curso**

`DELETE /api/admin/courses/{course_id}`

---

## 3. Gestão de Regulamentos (RF2.3)

**Auth:** Admin Geral

Ficheiros guardados em Object Storage.

### **3.1 Listar regulamentos**

`GET /api/admin/regulations`
Optional:

* `modality_id`

### **3.2 Upload de regulamento**

`POST /api/admin/regulations`
Multipart Body:

* `file` (obrigatório)
* `title` (obrigatório)
* `modality_id` (opcional)
* `description` (opcional)

### **3.3 Atualizar metadados**

`PUT /api/admin/regulations/{regulation_id}`
Body:

* `title` (opcional)
* `description` (opcional)
* `modality_id` (opcional)

### **3.4 Apagar regulamento**

`DELETE /api/admin/regulations/{regulation_id}`

---

## 4. Gestão de Modalidades (RF3)

**Auth:** Admin Geral

### **4.1 Listar modalidades**

`GET /api/admin/modalities`

### **4.2 Criar modalidade**

`POST /api/admin/modalities`
Body:

* `name` (obrigatório)
* `type` (“coletiva”, “individual”, “mista”) — obrigatório
* `scoring_schema` (opcional; JSON)

### **4.3 Atualizar modalidade**

`PUT /api/admin/modalities/{modality_id}`
Body:

* `name` (opcional)
* `type` (opcional)
* `scoring_schema` (opcional)

### **4.4 Remover modalidade**

`DELETE /api/admin/modalities/{modality_id}`

---

## 5. Gestão de Torneios (RF3)

Auth: Admin Geral

### **5.1 Listar torneios**

`GET /api/admin/tournaments`
Optional:

* `modality_id`
* `status` (draft, active, finished)

### **5.2 Criar torneio**

`POST /api/admin/tournaments`
Body:

* `modality_id` (obrigatório)
* `name` (obrigatório)
* `season_id` (obrigatório)
* `rules` (opcional)
* `teams` (lista de team_ids) (opcional)
* `start_date` (opcional)

### **5.3 Atualizar torneio**

`PUT /api/admin/tournaments/{tournament_id}`
Body:

* `name` (opcional)
* `rules` (opcional)
* `teams` (opcional)
* `start_date` (opcional)

### **5.4 Remover torneio**

`DELETE /api/admin/tournaments/{tournament_id}`

### **5.5 Terminar torneio**

`POST /api/admin/tournaments/{tournament_id}/finish`
Body:

* sem body
  Bloqueia edições + envia evento para ranking-service.

---

## 6. Gestão de Equipas (RF4)

Auth: **Administrador de Núcleo** (apenas do seu curso)

### **6.1 Listar equipas**

`GET /api/admin/teams`
Optional:

* `modality_id`
* `course_id` (ignorado — sempre course_id do token)
* `all` (boolean string: 'true' ou 'false') - retorna equipas de todos os cursos se 'true'

### **6.2 Criar equipa**

`POST /api/admin/teams`
Body:

* `modality_id` (obrigatório)
* `name` (opcional)
* `players` (lista de student_ids) (opcional)

### **6.3 Atualizar equipa**

`PUT /api/admin/teams/{team_id}`
Body:

* `name` (opcional)
* `players_add` (lista de student_ids)
* `players_remove` (lista de student_ids)

### **6.4 Remover equipa**

`DELETE /api/admin/teams/{team_id}`

---

## 7. Gestão de Estudantes (RF4)

**Nota:** Estudantes podem ser de dois tipos:
- `student` - Estudantes jogadores
- `technical_staff` - Equipa técnica (treinadores, professores, etc.)

### **7.1 Listar estudantes do curso**

`GET /api/admin/students`

Response inclui campo `member_type` ('student' ou 'technical_staff')

### **7.2 Criar estudante**

`POST /api/admin/students`
Body:

* `full_name` (obrigatório)
* `student_number` (obrigatório)
* `email` (opcional)
* `is_member` (opcional; default false)
* `member_type` (opcional; 'student' ou 'technical_staff'; default 'student')

### **7.3 Atualizar estudante**

`PUT /api/admin/students/{student_id}`
Body:

* `full_name` (opcional)
* `email` (opcional)
* `is_member` (opcional)
* `member_type` (opcional; 'student' ou 'technical_staff')

### **7.4 Remover estudante**

`DELETE /api/admin/students/{student_id}`

---

## 8. Gestão de Jogos (RF7)

Auth:

* **Admin Geral** → cria e edita agenda
* **Admin Núcleo** → apenas equipa, jogadores e ficha

### **8.1 Listar jogos**

`GET /api/admin/matches`
Optional:

* `modality_id`
* `tournament_id`
* `team_id`
* `course_id`
* `date`
* `status` (scheduled, finished)

### **8.2 Criar jogo**

`POST /api/admin/matches`
Body:

* `tournament_id` (obrigatório)
* `team_home_id` (obrigatório)
* `team_away_id` (obrigatório)
* `location` (obrigatório)
* `start_time` (obrigatório)

### **8.3 Atualizar jogo**

`PUT /api/admin/matches/{match_id}`
Body:

* `location` (opcional)
* `start_time` (opcional)
* `team_home_id` (opcional)
* `team_away_id` (opcional)

### **8.4 Registrar resultado**

`POST /api/admin/matches/{match_id}/result`
Body:

* `home_score` (obrigatório)
* `away_score` (obrigatório)

### **8.5 Atribuir jogadores ao jogo (RF7.1 / RF7.2)**

`POST /api/admin/matches/{match_id}/lineup`
Body:

* `team_id` (obrigatório)
* `players` (lista de player IDs - array de inteiros)

### **8.6 Adicionar comentários (RF7.3)**

`POST /api/admin/matches/{match_id}/comments`
Body:

* `message` (obrigatório)

### **8.7 Gerar ficha de jogo PDF**

`GET /api/admin/matches/{match_id}/sheet`
Retorna PDF (stream).

---

## 9. Épocas / Seasons (RF2.4)

### **9.1 Listar épocas**

`GET /api/admin/seasons`

Response:
```json
{
  "id": 1,
  "year": 2025,
  "status": "active"  // draft | active | finished
}
```

### **9.2 Criar época**

`POST /api/admin/seasons`
Body:

* `year` (obrigatório)

Response: Nova época criada com `status: "draft"`

### **9.3 Iniciar época**

`POST /api/admin/seasons/{season_id}/start`

**Nota:** Só pode existir uma época ativa de cada vez. Ao iniciar uma época, qualquer época ativa anterior é automaticamente terminada.

### **9.4 Terminar época**

`POST /api/admin/seasons/{season_id}/finish`

**Nota:** A época passará ao estado `finished` e não pode ser reaberta.

---

# 2. PUBLIC DATA API (READ MODEL API)

Usada por:

* **Utilizadores públicos**
* **Sem autenticação** (todos os endpoints são públicos)
* Apenas **leitura** da *read-model store* (Postgres + Redis).

**Prefixo**: `/api/public`

✅ **Todos os endpoints são públicos** — não requerem autenticação nem tokens.

---

## 1. Calendário Público (RF5.1)

### **1.1 Jogos por dia**

`GET /api/public/matches`
Optional query parameters:

* `date` (string, formato YYYY-MM-DD) - Filtrar por data exata
* `modality_id` (int) - Filtrar por modalidade
* `course_id` (int) - Filtrar por curso/núcleo
* `team_id` (int) - Filtrar por equipa
* `status` (string) - Filtrar por estado (scheduled, in_progress, finished, cancelled)
* `limit` (int, default 50) - Número de resultados
* `offset` (int, default 0) - Pular resultados

Retorna lista de jogos com:
- `id` (int)
- `tournament_id` (int)
- `tournament_name` (string)
- `team_home` (objeto):
  - `id` (int)
  - `name` (string)
  - `course_abbreviation` (string)
- `team_away` (objeto):
  - `id` (int)
  - `name` (string)
  - `course_abbreviation` (string)
- `modality` (objeto):
  - `id` (int)
  - `name` (string)
- `start_time` (datetime)
- `location` (string)
- `status` (string)
- `home_score` (int, opcional)
- `away_score` (int, opcional)

### **1.2 Jogos de hoje**

`GET /api/public/matches/today`

Retorna jogos agendados para o dia atual no mesmo formato do endpoint 1.1.

### **1.3 Detalhes de um jogo**

`GET /api/public/matches/{match_id}`

Retorna detalhes completos de um jogo com os mesmos campos do endpoint 1.1.

---

## 2. Resultados (RF5.2)

### **2.1 Resultados finais**

`GET /api/public/results`
Optional:

* `modality_id`
* `tournament_id`
* `course_id`

---

## 3. Classificações (RF5.3–5.5)

### **3.1 Classificação por modalidade**

`GET /api/public/rankings/modality/{modality_id}`
Optional query parameters:

* `season_id` (string) - Filtrar por época

Retorna classificação de uma modalidade específica com:
- `modality` (objeto com id e name)
- `season` (objeto com id, year, display_name)
- `rankings` (array de rankings de torneios dessa modalidade)

### **3.2 Classificação por curso**

`GET /api/public/rankings/course/{course_id}`
Optional query parameters:

* `season_id` (string) - Filtrar por época

Retorna classificação de um curso específico.

### **3.3 Classificação geral**

`GET /api/public/rankings/general`
Optional query parameters:

* `season_id` (string) - Filtrar por época específica (se não fornecido, retorna época ativa)

Retorna classificação geral com:
- `season` (objeto):
  - `id` (string)
  - `year` (int)
  - `display_name` (string)
- `rankings` (array de objetos):
  - `position` (int)
  - `course_id` (int)
  - `course_name` (string)
  - `course_short_code` (string)
  - `points` (int)
  - `played` (int) - Jogos disputados
  - `won` (int) - Vitórias
  - `drawn` (int) - Empates
  - `lost` (int) - Derrotas

### **3.4 Classificações de anos anteriores (RF5.7)**

`GET /api/public/rankings/general/history`
Optional:

* `season_id`

---

## 4. Torneios Públicos

### **4.1 Listar torneios**

`GET /api/public/tournaments`
Optional:

* `modality_id`
* `season_id`
* `status`

### **4.2 Detalhes de torneio**

`GET /api/public/tournaments/{tournament_id}`
Optional query params:
* `include_rankings` (boolean) - Se true, inclui classificações no retorno

Retorna detalhes do torneio incluindo:
- Informação da modalidade
- Informação da época
- Status (draft, active, finished)
- Data de início
- Número de equipas
- Rankings (se `include_rankings=true`)

### **4.3 Classificações de um torneio**

`GET /api/public/tournaments/{tournament_id}/rankings`

Retorna lista ordenada de equipas com:
- Posição
- Equipa (id, nome)
- Curso (id, nome, abreviatura)
- Pontos
- Jogos disputados
- Vitórias
- Empates
- Derrotas

---

## 5. Modalidades Públicas

### **5.1 Listar modalidades**

`GET /api/public/modalities`

Retorna lista de modalidades disponíveis:
- `id` (int)
- `name` (string) - Nome da modalidade (Futebol, Futsal, Andebol, Voleibol)
- `type` (string) - Tipo (coletiva, individual, mista)
- `scoring_schema` (dict, opcional) - Sistema de pontuação, ex: `{"win": 3, "draw": 1, "loss": 0}`

---

## 6. Cursos

### **6.1 Listar cursos**

`GET /api/public/courses`

---

## 7. Épocas/Seasons Públicas

### **7.1 Listar épocas**

`GET /api/public/seasons`

Retorna lista de épocas com:
- `id` (int)
- `year` (int)
- `status` (string) - Estado da época: `draft`, `active`, ou `finished`

---

## 8. Equipas Públicas

### **8.1 Listar equipas**

`GET /api/public/teams`
Optional:
* `course_id` - Filtrar por curso
* `modality_id` - Filtrar por modalidade

Retorna lista de equipas com informações do curso, modalidade e número de jogadores.

---

## 9. Regulamentos (RF5.6)

### **9.1 Listar regulamentos**

`GET /api/public/regulations`
Optional:

* `category` - Filtrar por categoria

Retorna lista de regulamentos com:
- `id` (UUID)
- `title` (string)
- `description` (string, opcional)
- `file_url` (string) - URL para download do PDF
- `category` (string, opcional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### **9.2 Obter ficheiro PDF**

`GET /api/public/regulations/{regulation_id}`

---

## 10. Histórico

### **10.1 Jogos de épocas anteriores**

`GET /api/public/matches/history`
Optional:

* `season_id`
* `modality_id`
* `course_id`

---
