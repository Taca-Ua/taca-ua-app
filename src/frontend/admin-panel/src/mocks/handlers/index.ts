import { modalityHandlers } from './modalities'
import { tournamentHandlers } from './tournaments'
import { teamHandlers } from './teams'
import { regulationHandlers } from './regulamentos'

export const handlers = [
  ...modalityHandlers,
  ...tournamentHandlers,
  ...teamHandlers,
  ...regulationHandlers,
]
