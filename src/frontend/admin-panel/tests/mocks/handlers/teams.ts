import { http, HttpResponse } from 'msw'

const API_BASE = '/api2/admin'

const athleteLookup: Record<string, { id: string; name: string; student_number: string }> = {
  'ath-1': { id: 'ath-1', name: 'Alice Almeida', student_number: '12345' },
  'ath-2': { id: 'ath-2', name: 'Bruno Barbosa', student_number: '67890' },
  'ath-3': { id: 'ath-3', name: 'Carla Costa', student_number: '13579' },
}

const initialTeams = [
  {
    id: 'team-1',
    name: 'Team A',
    modality: { id: 'mod-1', name: 'Futebol' },
    course: { id: 'c1', name: 'Course 1', abbreviation: 'C1' },
    players: [athleteLookup['ath-1']],
  },
  {
    id: 'team-2',
    name: 'Team B',
    modality: { id: 'mod-2', name: 'Atletismo' },
    course: { id: 'c2', name: 'Course 2', abbreviation: 'C2' },
    players: [athleteLookup['ath-2'], athleteLookup['ath-3']],
  },
]

let teams = structuredClone(initialTeams)

const modalityLookup: Record<string, { id: string; name: string }> = {
  'mod-1': { id: 'mod-1', name: 'Futebol' },
  'mod-2': { id: 'mod-2', name: 'Atletismo' },
}

const courseLookup: Record<string, { id: string; name: string; abbreviation: string }> = {
  c1: { id: 'c1', name: 'Course 1', abbreviation: 'C1' },
  c2: { id: 'c2', name: 'Course 2', abbreviation: 'C2' },
}

export const resetTeamHandlers = () => {
  teams = structuredClone(initialTeams)
}

export const teamHandlers = [
  http.get(`${API_BASE}/teams/`, ({ request }) => {
    const url = new URL(request.url)
    const modalityId = url.searchParams.get('modality_id')
    const courseId = url.searchParams.get('course_id')

    const filtered = teams.filter((team) => {
      const matchesModality = modalityId ? team.modality.id === modalityId : true
      const matchesCourse = courseId ? team.course.id === courseId : true
      return matchesModality && matchesCourse
    }).map(({ players, ...team }) => team)
    return HttpResponse.json(filtered)
  }),

  http.get(`${API_BASE}/teams/:id/`, ({ params }) => {
    const { id } = params
    const team = teams.find((item) => item.id === id)

    if (!team) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(team)
  }),

  http.post(`${API_BASE}/teams/`, async ({ request }) => {
    const payload = await request.json()
    const created = {
      id: `team-${teams.length + 1}`,
      name: payload.name ?? 'Nova Equipa',
      modality: modalityLookup[payload.modality_id] ?? { id: payload.modality_id, name: payload.modality_id },
      course: courseLookup[payload.course_id] ?? { id: payload.course_id, name: payload.course_id, abbreviation: payload.course_id },
      players: [],
    }

    teams = [created, ...teams]
    const { players, ...teamListItem } = created
    return HttpResponse.json(teamListItem, { status: 201 })
  }),

  http.put(`${API_BASE}/teams/:id/`, async ({ params, request }) => {
    const { id } = params
    const target = teams.find((item) => item.id === id)

    if (!target) {
      return new HttpResponse(null, { status: 404 })
    }

    const payload = await request.json()
    let updatedPlayers = [...target.players]

    if (Array.isArray(payload.players_remove)) {
      updatedPlayers = updatedPlayers.filter((player) => !payload.players_remove.includes(player.id))
    }

    if (Array.isArray(payload.players_add)) {
      payload.players_add.forEach((playerId: string) => {
        const player = athleteLookup[playerId]
        if (player && !updatedPlayers.some((existing) => existing.id === player.id)) {
          updatedPlayers.push(player)
        }
      })
    }

    const updated = {
      ...target,
      name: typeof payload.name === 'string' && payload.name.trim().length > 0 ? payload.name : target.name,
      modality: payload.modality_id ? (modalityLookup[payload.modality_id] ?? target.modality) : target.modality,
      course: payload.course_id ? (courseLookup[payload.course_id] ?? target.course) : target.course,
      players: updatedPlayers,
    }

    teams = teams.map((item) => (item.id === id ? updated : item))
    return HttpResponse.json(updated)
  }),

  http.delete(`${API_BASE}/teams/:id/`, ({ params }) => {
    const { id } = params
    teams = teams.filter((item) => item.id !== id)
    return new HttpResponse(null, { status: 204 })
  }),
]
