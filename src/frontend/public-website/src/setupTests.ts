import '@testing-library/jest-dom'
import { server } from './mocks/server'
import { resetNucleosHandlers } from './mocks/handlers/nucleos'
import { resetTeamsHandlers } from './mocks/handlers/teams'
import { resetRegulationsHandlers } from './mocks/handlers/regulations'
import { resetMatchesHandlers } from './mocks/handlers/matches'

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
  resetNucleosHandlers()
  resetTeamsHandlers()
  resetRegulationsHandlers()
  resetMatchesHandlers()
  server.resetHandlers()
})
afterAll(() => server.close())
