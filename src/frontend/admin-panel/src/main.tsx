import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import { router } from './routes'
import { AuthProvider } from './contexts/AuthProvider'
import { NotificationProvider } from './contexts/NotificationProvider'

createRoot(document.getElementById('root')!).render(
  <NotificationProvider>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </NotificationProvider>,
)
