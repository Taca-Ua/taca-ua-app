import type { ReactElement } from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ModalProvider } from '../src/contexts/ModalContext'
import { NotificationProvider } from '../src/contexts/NotificationProvider'
import { AuthContext, type AuthContextType } from '../src/contexts/AuthContext'

type RenderOptions = {
  initialEntries?: string[]
}

export function renderWithProviders(
  ui: ReactElement,
  { initialEntries = ['/'] }: RenderOptions = {},
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthContext.Provider
        value={
          {
            isLoading: false,
            isAuthenticated: true,
            token: 'test-token',
            roles: ['general_admin'],
            adminRole: 'general_admin',
            username: 'test-user',
            login: () => undefined,
            logout: () => undefined,
            hasRole: (role: any) => role === 'general_admin',
            isAdminGeneral: true,
            isAdminNucleo: false,
          } as AuthContextType
        }
      >
        <NotificationProvider>
          <ModalProvider>{ui}</ModalProvider>
        </NotificationProvider>
      </AuthContext.Provider>
    </MemoryRouter>,
  )
}
