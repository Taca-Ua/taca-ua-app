import { http, HttpResponse } from 'msw'

const API_BASE = '/api/public'

const initialTeams = [
  {
    team_id: 'team-1',
    team_name: 'Engenharia Informática A',
    modality_name: 'Futebol',
    course_name: 'Engenharia Informática',
    course_abbreviation: 'EI',
    nucleo_name: 'NEI',
  },
  {
    team_id: 'team-2',
    team_name: 'Engenharia Civil A',
    modality_name: 'Futebol',
    course_name: 'Engenharia Civil',
    course_abbreviation: 'EC',
    nucleo_name: 'NEC',
  },
  {
    team_id: 'team-3',
    team_name: 'Engenharia Informática B',
    modality_name: 'Voleibol',
    course_name: 'Engenharia Informática',
    course_abbreviation: 'EI',
    nucleo_name: 'NEI',
  },
]

let teams = structuredClone(initialTeams)

export const resetTeamsHandlers = () => {
  teams = structuredClone(initialTeams)
}

export const teamsHandlers = [
  http.get(`${API_BASE}/teams`, ({ request }) => {
    const url = new URL(request.url)
    const page = url.searchParams.get('page') || '1'
    const page_size = url.searchParams.get('page_size') || '20'

    return HttpResponse.json({
      items: teams,
      total: teams.length,
      page: parseInt(page),
      page_size: parseInt(page_size),
    })
  }),

  http.get(`${API_BASE}/teams/:teamId`, ({ params }) => {
    const { teamId } = params
    const team = teams.find((t) => t.team_id === teamId)

    if (!team) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json(team)
  }),
]
