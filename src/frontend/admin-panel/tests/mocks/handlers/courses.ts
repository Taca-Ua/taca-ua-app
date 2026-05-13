import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialCourses = [
  {
    id: 'course-1',
    name: 'Engenharia Informática',
    abbreviation: 'LEI',
    nucleo: {
      id: 'nucleo-1',
      name: 'Núcleo de Eletrónica e Computação',
      abbreviation: 'NEECT',
    },
  },
  {
    id: 'course-2',
    name: 'Engenharia Civil',
    abbreviation: 'LEC',
    nucleo: {
      id: 'nucleo-2',
      name: 'Núcleo de Estruturas',
      abbreviation: 'NES',
    },
  },
  {
    id: 'course-3',
    name: 'Matemática Aplicada',
    abbreviation: 'MA',
    nucleo: {
      id: 'nucleo-1',
      name: 'Núcleo de Eletrónica e Computação',
      abbreviation: 'NEECT',
    },
  },
]

let courses = structuredClone(initialCourses)

export const resetCourseHandlers = () => {
  courses = structuredClone(initialCourses)
}

const buildCourseDetail = (course: typeof initialCourses[number]) => ({
  ...course,
})

export const courseHandlers = [
  http.get(`${API_BASE}/courses/`, () => {
    return HttpResponse.json(courses)
  }),

  http.get(`${API_BASE}/courses/:id/`, ({ params }) => {
    const { id } = params
    const course = courses.find((item) => item.id === id)

    if (!course) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(buildCourseDetail(course))
  }),

  http.delete(`${API_BASE}/courses/:id/`, ({ params }) => {
    const { id } = params
    courses = courses.filter((item) => item.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),

  http.put(`${API_BASE}/courses/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = courses.find((item) => item.id === id)

    if (!target) {
      return new HttpResponse(null, { status: 404 })
    }

    const payload = await request.json() as {
      name?: string
      abbreviation?: string
      nucleo_id?: string
    }

    const updated = {
      ...target,
      name: typeof payload.name === 'string' && payload.name.trim().length > 0 ? payload.name : target.name,
      abbreviation: typeof payload.abbreviation === 'string' && payload.abbreviation.trim().length > 0 ? payload.abbreviation : target.abbreviation,
      nucleo: payload.nucleo_id === 'nucleo-2'
        ? {
            id: 'nucleo-2',
            name: 'Núcleo de Estruturas',
            abbreviation: 'NES',
          }
        : {
            id: 'nucleo-1',
            name: 'Núcleo de Eletrónica e Computação',
            abbreviation: 'NEECT',
          },
    }

    courses = courses.map((item) => (item.id === id ? updated : item))
    return HttpResponse.json(buildCourseDetail(updated))
  }),

  http.post(`${API_BASE}/courses/`, async ({ request }) => {
    const payload = await request.json() as {
      name?: string
      abbreviation?: string
      nucleo_id?: string
    }

    const created = {
      id: `course-${courses.length + 1}`,
      name: payload.name ?? 'Novo Curso',
      abbreviation: payload.abbreviation ?? 'NC',
      nucleo: payload.nucleo_id === 'nucleo-2'
        ? {
            id: 'nucleo-2',
            name: 'Núcleo de Estruturas',
            abbreviation: 'NES',
          }
        : {
            id: 'nucleo-1',
            name: 'Núcleo de Eletrónica e Computação',
            abbreviation: 'NEECT',
          },
    }

    courses = [created, ...courses]
    return HttpResponse.json(created, { status: 201 })
  }),
]
