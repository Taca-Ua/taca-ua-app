import { http, HttpResponse } from 'msw'

const API_BASE = '/api/public'

const initialMatches = [
  {
    match_id: 'match-1',
    location: 'Pavilhão A',
    status: 'scheduled',
    start_time: '2026-05-15T14:00:00Z',
    tournament_id: 'tournament-1',
    tournament_name: 'Taça UA 2026 - Futebol',
    modality_id: 'modality-1',
    modality_name: 'Futebol',
    participants: [
      { participant_id: '1', participant_name: 'Engenharia Informática A' },
      { participant_id: '2', participant_name: 'Engenharia Civil A' },
    ],
    results: null,
    participant_count: 2,
    comment_count: 0,
  },
  {
    match_id: 'match-2',
    location: 'Pavilhão B',
    status: 'scheduled',
    start_time: '2026-05-16T15:00:00Z',
    tournament_id: 'tournament-1',
    tournament_name: 'Taça UA 2026 - Futebol',
    modality_id: 'modality-1',
    modality_name: 'Futebol',
    participants: [
      { participant_id: '3', participant_name: 'Engenharia Informática B' },
      { participant_id: '4', participant_name: 'Engenharia Elétrica A' },
    ],
    results: null,
    participant_count: 2,
    comment_count: 0,
  },
  {
    match_id: 'match-3',
    location: 'Campo A',
    status: 'finished',
    start_time: '2026-05-17T16:00:00Z',
    tournament_id: 'tournament-2',
    tournament_name: 'Taça UA 2026 - Voleibol',
    modality_id: 'modality-2',
    modality_name: 'Voleibol',
    participants: [
      { participant_id: '5', participant_name: 'Engenharia Civil B' },
      { participant_id: '6', participant_name: 'Engenharia Mecânica A' },
    ],
    results: [{ result_id: '1', score: '2-1' }],
    participant_count: 2,
    comment_count: 0,
  },
]

let matches = structuredClone(initialMatches)

export const resetMatchesHandlers = () => {
  matches = structuredClone(initialMatches)
}

export const matchesHandlers = [
  http.get(`${API_BASE}/matches`, ({ request }) => {
    const url = new URL(request.url)
    const page = url.searchParams.get('page') || '1'
    const page_size = url.searchParams.get('page_size') || '20'

    return HttpResponse.json({
      items: matches,
      total: matches.length,
      page: parseInt(page),
      page_size: parseInt(page_size),
    })
  }),

  http.get(`${API_BASE}/matches/:matchId`, ({ params }) => {
    const { matchId } = params
    const match = matches.find((m) => m.match_id === matchId)

    if (!match) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(match)
  }),
]
