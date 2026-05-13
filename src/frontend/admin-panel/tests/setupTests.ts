import '@testing-library/jest-dom'
import 'whatwg-fetch'
import { server } from './mocks/server'
import { resetModalityHandlers } from './mocks/handlers/modalities'
import { resetRegulationHandlers } from './mocks/handlers/regulamentos'
import { resetNucleosHandlers } from './mocks/handlers/nucleos'
import { resetCourseHandlers } from './mocks/handlers/courses'
import { resetAthletesHandlers } from './mocks/handlers/athletes'
import { resetStaffHandlers } from './mocks/handlers/staff'
import { resetTournamentHandlers } from './mocks/handlers/tournaments'
import { resetMatchHandlers } from './mocks/handlers/matches'
import { resetTeamHandlers } from './mocks/handlers/teams'


const localStorageMock = (function () {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString() },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})


beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => {
  resetModalityHandlers()
  resetRegulationHandlers()
  resetNucleosHandlers()
  resetCourseHandlers()
  resetAthletesHandlers()
  resetStaffHandlers()
  resetTournamentHandlers()
  resetMatchHandlers()
  resetTeamHandlers()
  server.resetHandlers()
})
afterAll(() => server.close())
