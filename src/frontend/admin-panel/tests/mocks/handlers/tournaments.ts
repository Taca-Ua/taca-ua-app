import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialTournaments = [
  {
    id: 't1',
    name: 'Torneio A',
    status: 'active',
    modality: { id: 'mod-1', name: 'Futebol' },
    start_date: '2026-05-01T00:00:00Z',
    competitor_type: 'team',
    competitors: [
      { id: 'comp-1', entity_id: 'team-1', name: 'Team A', course_name: 'Engenharia Informática' },
      { id: 'comp-2', entity_id: 'team-2', name: 'Team B', course_name: 'Engenharia Civil' },
    ],
    scoring_format: {
      name: 'Pontos padrão',
      rank: '1',
      points: [3, 1, 0],
    },
  },
  {
    id: 't2',
    name: 'Torneio B',
    status: 'draft',
    modality: { id: 'mod-2', name: 'Atletismo' },
    start_date: null,
    competitor_type: 'athlete',
    competitors: [],
    scoring_format: {
      name: 'Pontos padrão',
      rank: '1',
      points: [10, 8, 6],
    },
  },
]

let tournaments = structuredClone(initialTournaments)

const modalityNames: Record<string, { id: string; name: string }> = {
  'mod-1': { id: 'mod-1', name: 'Futebol' },
  'mod-2': { id: 'mod-2', name: 'Atletismo' },
}

export const resetTournamentHandlers = () => {
  tournaments = structuredClone(initialTournaments)
}

export const tournamentHandlers = [
  http.get(`${API_BASE}/tournaments/`, ({ request }) => {
    const url = new URL(request.url)
    const modalityId = url.searchParams.get('modality_id')

    const filtered = modalityId ? tournaments.filter(t => t.modality.id === modalityId) : tournaments
    return HttpResponse.json(filtered)
  }),

  http.get(`${API_BASE}/tournaments/:id/`, ({ params }) => {
    const { id } = params
    const tournament = tournaments.find((item) => item.id === id)

    if (!tournament) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(tournament)
  }),

  http.post(`${API_BASE}/tournaments/`, async ({ request }) => {
    const payload = await request.json()
    const created = {
      id: `t-${tournaments.length + 1}`,
      name: payload.name ?? 'Novo Torneio',
      status: 'draft',
      modality: modalityNames[payload.modality_id] ?? { id: payload.modality_id, name: payload.modality_id },
      start_date: null,
      competitor_type: 'team',
      competitors: [],
      scoring_format: {
        name: 'Pontos padrão',
        rank: '1',
        points: [3, 1, 0],
      },
    }

    tournaments = [created, ...tournaments]
    return HttpResponse.json(created, { status: 201 })
  }),

  http.put(`${API_BASE}/tournaments/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = tournaments.find((item) => item.id === id)

    if (!target) {
      return new HttpResponse(null, { status: 404 })
    }

    const payload = await request.json()
    const updated = {
      ...target,
      name: typeof payload.name === 'string' && payload.name.trim().length > 0 ? payload.name : target.name,
      start_date: typeof payload.start_date === 'string' && payload.start_date.trim().length > 0 ? payload.start_date : target.start_date,
      status: payload.status ?? target.status,
    }

    tournaments = tournaments.map((item) => (item.id === id ? updated : item))
    return HttpResponse.json(updated)
  }),

  http.delete(`${API_BASE}/tournaments/:id/`, ({ params }) => {
    const { id } = params
    tournaments = tournaments.filter((item) => item.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(`${API_BASE}/tournaments/:id/finish/`, async ({ params, request }) => {
    const { id } = params
    const target = tournaments.find((item) => item.id === id)

    if (!target) {
      return new HttpResponse(null, { status: 404 })
    }

    await request.json()
    const updated = {
      ...target,
      status: 'finished',
    }

    tournaments = tournaments.map((item) => (item.id === id ? updated : item))
    return HttpResponse.json(updated)
  }),
]
