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
]
