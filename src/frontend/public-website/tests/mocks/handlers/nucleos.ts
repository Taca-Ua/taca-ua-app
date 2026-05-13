import { http, HttpResponse } from 'msw'

const API_BASE = '/api/public'

const initialNucleos = [
  {
    nucleo_id: 'nuc-1',
    name: 'Núcleo de Engenharia Informática',
    abbreviation: 'NEI',
    logo_url: 'https://example.com/logo1.png',
  },
  {
    nucleo_id: 'nuc-2',
    name: 'Núcleo de Engenharia Civil',
    abbreviation: 'NEC',
    logo_url: 'https://example.com/logo2.png',
  },
  {
    nucleo_id: 'nuc-3',
    name: 'Núcleo de Engenharia Elétrica',
    abbreviation: 'NEE',
    logo_url: null,
  },
]

let nucleos = structuredClone(initialNucleos)

export const resetNucleosHandlers = () => {
  nucleos = structuredClone(initialNucleos)
}

export const nucleosHandlers = [
  http.get(`${API_BASE}/nucleos`, ({ request }) => {
    const url = new URL(request.url)
    const page = url.searchParams.get('page') || '1'
    const page_size = url.searchParams.get('page_size') || '10'

    return HttpResponse.json({
      items: nucleos,
      total: nucleos.length,
      page: parseInt(page),
      page_size: parseInt(page_size),
    })
  }),

  http.get(`${API_BASE}/nucleos/:nucleoId`, ({ params }) => {
    const { nucleoId } = params
    const nucleo = nucleos.find((n) => n.nucleo_id === nucleoId)

    if (!nucleo) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(nucleo)
  }),
]
