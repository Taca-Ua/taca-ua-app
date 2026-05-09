import '@testing-library/jest-dom'
import 'whatwg-fetch'
import { server } from './mocks/server'
import { resetModalityHandlers } from './mocks/handlers/modalities'


// Create a simple mock for localStorage
const localStorageMock = (function () {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString() },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

// Assign it to the global window object
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})


// Start MSW before all tests and close after
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => {
  resetModalityHandlers()
  server.resetHandlers()
})
afterAll(() => server.close())
