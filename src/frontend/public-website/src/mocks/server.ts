import { setupServer } from 'msw/node'
import { nucleosHandlers } from './handlers/nucleos'
import { teamsHandlers } from './handlers/teams'
import { regulationsHandlers } from './handlers/regulations'
import { matchesHandlers } from './handlers/matches'

export const server = setupServer(
  ...nucleosHandlers,
  ...teamsHandlers,
  ...regulationsHandlers,
  ...matchesHandlers,
)
