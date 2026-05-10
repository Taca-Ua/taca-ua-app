import '@testing-library/jest-dom'
import 'whatwg-fetch'
import { server } from './mocks/server'
import { resetModalityHandlers } from './mocks/handlers/modalities'
import { resetRegulationHandlers } from './mocks/handlers/regulamentos'


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
  server.resetHandlers()
})
afterAll(() => server.close())
