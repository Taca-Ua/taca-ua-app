import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const initialStaff = [
  { id: 'staff-1', full_name: 'Diana Duarte', staff_number: 'S100', contact: 'diana@example.com' },
  { id: 'staff-2', full_name: 'Eduardo Esteves', staff_number: 'S101', contact: 'eduardo@example.com' },
]

let staff = structuredClone(initialStaff)

export const resetStaffHandlers = () => {
  staff = structuredClone(initialStaff)
}

export const staffHandlers = [
  http.get(`${API_BASE}/staff/`, ({ request }) => {
    const url = new URL(request.url)
    const params = Object.fromEntries(url.searchParams.entries())
    let out = staff
    if (params.staff_number) {
      out = out.filter(s => s.staff_number === params.staff_number)
    }
    return HttpResponse.json(out)
  }),

  http.get(`${API_BASE}/staff/:id/`, ({ params }) => {
    const { id } = params
    const member = staff.find((s) => s.id === id)
    if (!member) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(member)
  }),

  http.post(`${API_BASE}/staff/`, async ({ request }) => {
    const payload = await request.json()
    const created = {
      id: `staff-${staff.length + 1}`,
      full_name: payload.full_name ?? 'Novo Staff',
      staff_number: payload.staff_number ?? `S${100 + staff.length}`,
      contact: payload.contact ?? '',
    }
    staff = [created, ...staff]
    return HttpResponse.json(created, { status: 201 })
  }),

  http.put(`${API_BASE}/staff/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = staff.find((s) => s.id === id)
    if (!target) return new HttpResponse(null, { status: 404 })
    const payload = await request.json()
    const updated = {
      ...target,
      full_name: typeof payload.full_name === 'string' ? payload.full_name : target.full_name,
      staff_number: typeof payload.staff_number === 'string' ? payload.staff_number : target.staff_number,
      contact: typeof payload.contact === 'string' ? payload.contact : target.contact,
    }
    staff = staff.map(s => s.id === id ? updated : s)
    return HttpResponse.json(updated)
  }),

  http.delete(`${API_BASE}/staff/:id/`, ({ params }) => {
    const { id } = params
    staff = staff.filter(s => s.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),
]
