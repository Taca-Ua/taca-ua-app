import { modalityHandlers } from './modalities'
import { tournamentHandlers } from './tournaments'
import { teamHandlers } from './teams'

export const handlers = [
  ...modalityHandlers,
  ...tournamentHandlers,
  ...teamHandlers,
]
