import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

export const teamHandlers = [
  http.get(`${API_BASE}/teams/`, ({ request }) => {
    const url = new URL(request.url)
    const modalityId = url.searchParams.get('modality_id')

    const all = [
      { id: 'team-1', name: 'Team A', modality: { id: 'mod-1', name: 'Futebol' }, course: { id: 'c1', name: 'Course 1', abbreviation: 'C1' } },
      { id: 'team-2', name: 'Team B', modality: { id: 'mod-2', name: 'Atletismo' }, course: { id: 'c2', name: 'Course 2', abbreviation: 'C2' } },
    ]

    const filtered = modalityId ? all.filter(t => t.modality.id === modalityId) : all
    return HttpResponse.json(filtered)
  }),
]
