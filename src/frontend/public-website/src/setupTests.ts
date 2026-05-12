import '@testing-library/jest-dom'
import { server } from './mocks/server'
import { resetNucleosHandlers } from './mocks/handlers/nucleos'

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
  server.resetHandlers()
})
afterAll(() => server.close())
