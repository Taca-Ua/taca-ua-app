import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import { router } from './routes'
import { AuthProvider } from './contexts/AuthProvider'
import { KeycloakProvider } from './auth/KeycloakProvider'

createRoot(document.getElementById('root')!).render(
  <StrictMode>

    <KeycloakProvider>

      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>

    </KeycloakProvider>
  </StrictMode>,
)
