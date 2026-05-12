import { setupServer } from 'msw/node'
import { nucleosHandlers } from './handlers/nucleos'

export const server = setupServer(...nucleosHandlers)
