import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialModalities = [
  {
    id: 'mod-1',
    name: 'Futebol',
    modality_type: {
      id: 'type-team',
      name: 'Coletiva',
    },
  },
  {
    id: 'mod-2',
    name: 'Atletismo',
    modality_type: {
      id: 'type-individual',
      name: 'Individual',
    },
  },
]

let modalities = structuredClone(initialModalities)

export const resetModalityHandlers = () => {
  modalities = structuredClone(initialModalities)
}

export const modalityHandlers = [
  http.get(`${API_BASE}/modalities/`, () => {
    return HttpResponse.json(modalities)
  }),

  http.get(`${API_BASE}/modalities/:id/`, ({ params }) => {
    const { id } = params
    const modality = modalities.find((item) => item.id === id)

    if (!modality) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json({
      ...modality,
    })
  }),

  http.delete(`${API_BASE}/modalities/:id/`, ({ params }) => {
    const { id } = params
    modalities = modalities.filter((item) => item.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),
]
