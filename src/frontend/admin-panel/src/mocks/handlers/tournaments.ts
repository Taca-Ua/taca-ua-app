import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

export const tournamentHandlers = [
  http.get(`${API_BASE}/tournaments/`, ({ request }) => {
    const url = new URL(request.url)
    const modalityId = url.searchParams.get('modality_id')

    const all = [
      { id: 't1', name: 'Torneio A', modality: { id: 'mod-1', name: 'Futebol' }, status: 'active', start_date: null },
      { id: 't2', name: 'Torneio B', modality: { id: 'mod-2', name: 'Atletismo' }, status: 'draft', start_date: null },
    ]

    const filtered = modalityId ? all.filter(t => t.modality.id === modalityId) : all
    return HttpResponse.json(filtered)
  }),
]
