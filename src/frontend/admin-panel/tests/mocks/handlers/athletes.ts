import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialAthletes = [
  {
    id: 'ath-1',
    full_name: 'Alice Almeida',
    student_number: '12345',
    is_member: true,
    course: { id: 'course-1', name: 'Engenharia Informática', abbreviation: 'LEI' },
  },
  {
    id: 'ath-2',
    full_name: 'Bruno Barbosa',
    student_number: '67890',
    is_member: false,
    course: { id: 'course-2', name: 'Engenharia Civil', abbreviation: 'LEC' },
  },
  {
    id: 'ath-3',
    full_name: 'Carla Costa',
    student_number: '13579',
    is_member: false,
    course: { id: 'course-1', name: 'Engenharia Informática', abbreviation: 'LEI' },
  },
]

let athletes = structuredClone(initialAthletes)

export const resetAthletesHandlers = () => {
  athletes = structuredClone(initialAthletes)
}

export const athletesHandlers = [
  http.get(`${API_BASE}/athletes/`, ({ request }) => {
    // support simple filtering by query params if present
    const url = new URL(request.url)
    const params = Object.fromEntries(url.searchParams.entries())
    let out = athletes
    if (params.course_id) {
      out = out.filter(a => a.course.id === params.course_id)
    }
    return HttpResponse.json(out)
  }),

  http.get(`${API_BASE}/athletes/:id/`, ({ params }) => {
    const { id } = params
    const ath = athletes.find(a => a.id === id)
    if (!ath) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(ath)
  }),

  http.post(`${API_BASE}/athletes/`, async ({ request }) => {
    const payload = await request.json()
    const created = {
      id: `ath-${athletes.length + 1}`,
      full_name: payload.full_name ?? 'Novo Atleta',
      student_number: payload.student_number ?? '00000',
      is_member: payload.is_member ?? false,
      course: payload.course_id === 'course-2' ? { id: 'course-2', name: 'Engenharia Civil', abbreviation: 'LEC' } : { id: 'course-1', name: 'Engenharia Informática', abbreviation: 'LEI' },
    }
    athletes = [created, ...athletes]
    return HttpResponse.json(created, { status: 201 })
  }),

  http.put(`${API_BASE}/athletes/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = athletes.find(a => a.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })
    const payload = await request.json()
    const updated = {
      ...target,
      full_name: typeof payload.full_name === 'string' ? payload.full_name : target.full_name,
      student_number: typeof payload.student_number === 'string' ? payload.student_number : target.student_number,
      is_member: typeof payload.is_member === 'boolean' ? payload.is_member : target.is_member,
      course: payload.course_id === 'course-2' ? { id: 'course-2', name: 'Engenharia Civil', abbreviation: 'LEC' } : target.course,
    }
    athletes = athletes.map(a => a.id === id ? updated : a)
    return HttpResponse.json(updated)
  }),

  http.delete(`${API_BASE}/athletes/:id/`, ({ params }) => {
    const { id } = params
    athletes = athletes.filter(a => a.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(`${API_BASE}/athletes/sync-membership/`, async ({ request }) => {
    const payload = await request.json()
    const numbers: string[] = payload.student_numbers || []
    let set_as_member = 0
    let reset_to_non_member = 0
    // set matched numbers as members
    athletes = athletes.map(a => {
      if (numbers.includes(a.student_number)) {
        if (!a.is_member) set_as_member++
        return { ...a, is_member: true }
      }
      if (a.is_member) {
        reset_to_non_member++
        return { ...a, is_member: false }
      }
      return a
    })

    return HttpResponse.json({ participants_in_scope: athletes.length, reset_to_non_socio: reset_to_non_member, set_as_socio: set_as_member, unmatched_numbers: numbers.filter(n => !athletes.some(a=>a.student_number===n)) })
  }),
]
