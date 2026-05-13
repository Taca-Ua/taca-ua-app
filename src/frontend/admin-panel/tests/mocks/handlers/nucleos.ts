import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialNucleos = [
  {
    id: 'nucleo-1',
    name: 'Núcleo de Eletrônica e Computação',
    abbreviation: 'NEECT',
    logo_url: 'https://example.com/neect-logo.png',
  },
  {
    id: 'nucleo-2',
    name: 'Núcleo de Estruturas',
    abbreviation: 'NES',
    logo_url: 'https://example.com/nes-logo.png',
  },
  {
    id: 'nucleo-3',
    name: 'Núcleo de Energias',
    abbreviation: 'NEN',
    logo_url: 'https://example.com/nen-logo.png',
  },
]

let nucleos = structuredClone(initialNucleos)

export const resetNucleosHandlers = () => {
  nucleos = structuredClone(initialNucleos)
}

export const nucleosHandlers = [
  http.get(`${API_BASE}/nucleos/`, () => {
    return HttpResponse.json(nucleos)
  }),

  http.get(`${API_BASE}/nucleos/:id/`, ({ params }) => {
    const { id } = params
    const nucleo = nucleos.find((item) => item.id === id)

    if (!nucleo) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json({
      ...nucleo,
      courses: [
        { id: 'course-1', name: 'Mestrado Integrado em Engenharia Eletrónica', abbreviation: 'MIEE' },
        { id: 'course-2', name: 'Mestrado em Computação', abbreviation: 'MC' },
      ],
    })
  }),

  http.delete(`${API_BASE}/nucleos/:id/`, ({ params }) => {
    const { id } = params
    nucleos = nucleos.filter((item) => item.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),

  http.put(`${API_BASE}/nucleos/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = nucleos.find((item) => item.id === id)

    if (!target) {
      return new HttpResponse(null, { status: 404 })
    }

    const formData = await request.formData()
    const name = formData.get('name')
    const abbreviation = formData.get('abbreviation')

    const updated = {
      ...target,
      name: typeof name === 'string' && name.trim().length > 0 ? name : target.name,
      abbreviation: typeof abbreviation === 'string' && abbreviation.trim().length > 0 ? abbreviation : target.abbreviation,
    }

    nucleos = nucleos.map((item) => (item.id === id ? updated : item))
    return HttpResponse.json({
      ...updated,
      courses: [
        { id: 'course-1', name: 'Mestrado Integrado em Engenharia Eletrónica', abbreviation: 'MIEE' },
        { id: 'course-2', name: 'Mestrado em Computação', abbreviation: 'MC' },
      ],
    })
  }),
]
