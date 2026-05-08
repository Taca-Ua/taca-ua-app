import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

export const handlers = [
  // Your existing tournament handler
  http.get(`${API_BASE}/tournaments/:id/`, ({ params }) => {
    const { id } = params
    return HttpResponse.json({
      id,
      name: `Mock Tournament ${id}`,
      status: 'active',
      modality: { id: '1', name: 'Basketball' },
      competitor_type: 'team',
      competitors: [],
      scoring_format: { name: 'points', rank: 'desc', points: [3, 2, 1] },
    })
  }),

  // ADD THIS: Handler for the matches list
  http.get(`${API_BASE}/matches/`, ({ request }) => {
    const url = new URL(request.url)
    const tournamentId = url.searchParams.get('tournament_id')

    return HttpResponse.json([
      {
        id: 'm1',
        tournament_id: tournamentId,
        date: '2024-05-20T10:00:00Z',
        location: 'Court A',
        home_team: { name: 'Team A' },
        away_team: { name: 'Team B' },
        status: 'scheduled'
      }
    ])
  }),
]
