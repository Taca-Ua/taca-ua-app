import { http, HttpResponse } from 'msw'

const API_BASE = '/api/public'

const initialRegulations = [
  {
    id: 'reg-1',
    title: 'Regulamento de Futebol',
    description: 'Regulamento geral para as competições de futebol',
    file_url: 'https://example.com/futebol.pdf',
  },
  {
    id: 'reg-2',
    title: 'Regulamento de Voleibol',
    description: 'Regulamento geral para as competições de voleibol',
    file_url: 'https://example.com/voleibol.pdf',
  },
  {
    id: 'reg-3',
    title: 'Regulamento de Atletismo',
    description: 'Regulamento geral para as competições de atletismo',
    file_url: 'https://example.com/atletismo.pdf',
  },
]

let regulations = structuredClone(initialRegulations)

export const resetRegulationsHandlers = () => {
  regulations = structuredClone(initialRegulations)
}

export const regulationsHandlers = [
  http.get(`${API_BASE}/regulations`, () => {
    return HttpResponse.json(regulations)
  }),
]
