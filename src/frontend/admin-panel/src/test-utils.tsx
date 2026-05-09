import type { ReactElement } from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ModalProvider } from './contexts/ModalContext'
import { NotificationProvider } from './contexts/NotificationProvider'

type RenderOptions = {
  initialEntries?: string[]
}

export function renderWithProviders(
  ui: ReactElement,
  { initialEntries = ['/'] }: RenderOptions = {},
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <NotificationProvider>
        <ModalProvider>{ui}</ModalProvider>
      </NotificationProvider>
    </MemoryRouter>,
  )
}
