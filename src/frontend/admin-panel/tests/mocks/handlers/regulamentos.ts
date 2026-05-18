import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialRegulations = [
  {
    id: 'reg-1',
    title: 'Regulamento Geral',
    file_url: 'https://example.com/reg-1.pdf',
    description: 'Regras gerais da competicao.',
    created_at: '2026-01-10T09:00:00Z',
  },
  {
    id: 'reg-2',
    title: 'Guia de Arbitragem',
    file_url: 'https://example.com/reg-2.pdf',
    description: 'Normas para arbitragem.',
    created_at: '2026-01-12T09:00:00Z',
  },
]

let regulations = structuredClone(initialRegulations)

export const resetRegulationHandlers = () => {
  regulations = structuredClone(initialRegulations)
}

export const regulationHandlers = [
  http.get(`${API_BASE}/regulations/`, () => {
    return HttpResponse.json(regulations)
  }),

  http.get(`${API_BASE}/regulations/:id/`, ({ params }) => {
    const { id } = params
    const regulation = regulations.find((item) => item.id === id)

    if (!regulation) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(regulation)
  }),

  http.delete(`${API_BASE}/regulations/:id/`, ({ params }) => {
    const { id } = params
    regulations = regulations.filter((item) => item.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),

  http.put(`${API_BASE}/regulations/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = regulations.find((item) => item.id === id)

    if (!target) {
      return new HttpResponse(null, { status: 404 })
    }

    const formData = await request.formData()
    const title = formData.get('title')
    const description = formData.get('description')

    const updated = {
      ...target,
      title: typeof title === 'string' && title.trim().length > 0 ? title : target.title,
      description: typeof description === 'string' ? description : target.description,
    }

    regulations = regulations.map((item) => (item.id === id ? updated : item))
    return HttpResponse.json(updated)
  }),
]
