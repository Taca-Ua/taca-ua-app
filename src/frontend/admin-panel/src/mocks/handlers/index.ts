import { modalityHandlers } from './modalities'
import { tournamentHandlers } from './tournaments'
import { teamHandlers } from './teams'
import { regulationHandlers } from './regulamentos'
import { nucleosHandlers } from './nucleos'
import { courseHandlers } from './courses'
import { athletesHandlers } from './athletes'
import { staffHandlers } from './staff'
import { matchHandlers } from './matches'

export const handlers = [
  ...modalityHandlers,
  ...tournamentHandlers,
  ...teamHandlers,
  ...regulationHandlers,
  ...nucleosHandlers,
  ...courseHandlers,
  ...athletesHandlers,
  ...staffHandlers,
  ...tournamentHandlers,
  ...matchHandlers,
]
