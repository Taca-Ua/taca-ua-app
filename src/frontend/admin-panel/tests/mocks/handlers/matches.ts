import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialMatches = [
  {
    id: 'match-1',
    tournament_id: 't1',
    location: 'Pavilhão A',
    start_time: '2026-05-10T10:00:00Z',
    status: 'scheduled',
    participants: [
      { id: 'p1', entity_id: 'team-1', name: 'Team A', score: null, position: null },
      { id: 'p2', entity_id: 'team-2', name: 'Team B', score: null, position: null },
    ],
    comments: [],
    lineups: [],
  },
]

let matches = structuredClone(initialMatches)

export const resetMatchHandlers = () => {
  matches = structuredClone(initialMatches)
}

export const matchHandlers = [
  http.get(`${API_BASE}/matches/`, ({ request }) => {
    const url = new URL(request.url)
    const tournamentId = url.searchParams.get('tournament_id')
    const status = url.searchParams.get('status')

    let filtered = matches
    if (tournamentId) {
      filtered = filtered.filter((item) => item.tournament_id === tournamentId)
    }
    if (status) {
      filtered = filtered.filter((item) => item.status === status)
    }

    return HttpResponse.json(filtered)
  }),

  http.get(`${API_BASE}/matches/:id/`, ({ params }) => {
    const { id } = params
    const match = matches.find((m) => m.id === id)
    if (!match) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(match)
  }),

  http.delete(`${API_BASE}/matches/:id/`, ({ params }) => {
    const { id } = params
    matches = matches.filter((m) => m.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(`${API_BASE}/matches/:id/comments/`, async ({ params, request }) => {
    const { id } = params
    const payload = await request.json()
    const target = matches.find((m) => m.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })

    const comment = {
      id: `c-${Date.now()}`,
      message: payload.message ?? '',
      author_name: 'Test User',
      can_edit: true,
    }
    target.comments = [ ...(target.comments || []), comment ]
    matches = matches.map((m) => (m.id === id ? target : m))
    return HttpResponse.json(target)
  }),

  http.delete(`${API_BASE}/matches/:id/comments/:commentId/`, ({ params }) => {
    const { id, commentId } = params
    const target = matches.find((m) => m.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })
    target.comments = (target.comments || []).filter((c) => c.id !== commentId)
    matches = matches.map((m) => (m.id === id ? target : m))
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(`${API_BASE}/matches/:id/lineups/`, async ({ params, request }) => {
    const { id } = params
    const payload = await request.json()
    const target = matches.find((m) => m.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })

    const lineup = {
      participant_id: payload.participant,
      lineup: (payload.players || []).map((p: string, idx: number) => ({
        player_id: p,
        player_name: `Player ${idx + 1}`,
        player_course: 'Course X',
        is_starter: true,
      })),
    }

    // replace or add
    target.lineups = [ ...(target.lineups || []).filter((l) => l.participant_id !== lineup.participant_id), lineup ]
    matches = matches.map((m) => (m.id === id ? target : m))
    return HttpResponse.json(target)
  }),

  http.put(`${API_BASE}/matches/:id/lineups/`, async ({ params, request }) => {
    const { id } = params
    const payload = await request.json()
    const target = matches.find((m) => m.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })

    const participant = payload.participant
    const updated = {
      participant_id: participant,
      lineup: (payload.players || []).map((p: any, idx: number) => ({
        player_id: p.player_id ?? `p${idx}`,
        player_name: p.player_name ?? `Player ${idx + 1}`,
        player_course: p.player_course ?? 'Course X',
        is_starter: !!p.is_starter,
      })),
    }

    target.lineups = [ ...(target.lineups || []).filter((l) => l.participant_id !== participant), updated ]
    matches = matches.map((m) => (m.id === id ? target : m))
    return HttpResponse.json(target)
  }),

  http.post(`${API_BASE}/matches/:id/results/`, async ({ params, request }) => {
    const { id } = params
    const payload = await request.json()
    const target = matches.find((m) => m.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })

    if (payload.participant_results) {
      payload.participant_results.forEach((r: any) => {
        const p = target.participants.find((part) => part.id === r.participant_id)
        if (p) {
          p.score = r.score ?? p.score
          p.position = r.position ?? p.position
        }
      })
    }
    if (payload.status) target.status = payload.status

    matches = matches.map((m) => (m.id === id ? target : m))
    return HttpResponse.json(target)
  }),
]
