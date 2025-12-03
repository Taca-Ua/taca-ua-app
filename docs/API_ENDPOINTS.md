# Importante

* Incluo apenas endpoints REST finais — **não incluo endpoints internos dos microservices**, que não são expostos externamente.
* Para cada endpoint coloco:

  * **Método**
  * **Path**
  * **Query params opcionais**
  * **Body (com campos obrigatórios e opcionais)**

# 1. COMPETITION API (ADMIN API)

Usada por:

* **Administrador Geral**
* **Administrador de Núcleo**
* Com autenticação **Keycloak** (RBAC).

A Competition API apenas **recebe comandos** (write-model), que depois sao processados internamente por vários micro-serviços.

**Prefixo base**: `/api/admin`

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

### **7.1 Listar estudantes do curso**

`GET /api/admin/students`

### **7.2 Criar estudante**

`POST /api/admin/students`
Body:

* `full_name` (obrigatório)
* `student_number` (obrigatório)
* `email` (opcional)
* `is_member` (opcional; default false)

### **7.3 Atualizar estudante**

`PUT /api/admin/students/{student_id}`
Body:

* `full_name` (opcional)
* `email` (opcional)
* `is_member` (opcional)

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
* `players` (lista de `{player_id, jersey_number}`)

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

### **9.2 Criar época**

`POST /api/admin/seasons`
Body:

* `year` (obrigatório)

### **9.3 Iniciar época**

`POST /api/admin/seasons/{season_id}/start`

### **9.4 Terminar época**

`POST /api/admin/seasons/{season_id}/finish`

---

# 2. PUBLIC DATA API (READ MODEL API)

Usada por:

* **Utilizadores públicos**
* **Sem autenticação**
* Apenas **leitura** da *read-model store* (Postgres + Redis).

**Prefixo**: `/api/public`
Sem autenticação.

---

## 1. Calendário Público (RF5.1)

### **1.1 Jogos por dia**

`GET /api/public/matches`
Optional:

* `date`
* `modality_id`
* `course_id`
* `team_id`
* `status`
* `limit`, `offset`

### **1.2 Jogos de hoje**

`GET /api/public/matches/today`

### **1.3 Detalhes de um jogo**

`GET /api/public/matches/{match_id}`

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

### **3.2 Classificação por curso**

`GET /api/public/rankings/course/{course_id}`

### **3.3 Classificação geral**

`GET /api/public/rankings/general`

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

---

## 6. Cursos

### **6.1 Listar cursos**

`GET /api/public/courses`

---

## 7. Épocas/Seasons Públicas

### **7.1 Listar épocas**

`GET /api/public/seasons`

Retorna lista de épocas com:
- `id` (UUID)
- `year` (int)
- `display_name` (string)
- `is_active` (boolean)

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
