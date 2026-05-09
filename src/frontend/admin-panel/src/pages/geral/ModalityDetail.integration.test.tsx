import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { expect, vi } from 'vitest'
import ModalidadeDetail from './ModalityDetail'
import Modalities from './Modalities'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

test('loads modality, shows tournaments and teams, and deletes modality via confirm modal', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/modalidades/:id" element={<ModalidadeDetail />} />
      <Route path="/modalidades" element={<Modalities />} />
    </Routes>,
    { initialEntries: ['/modalidades/mod-1'] },
  )

  expect(await screen.findByText('Futebol')).toBeInTheDocument()
  expect(screen.getByText('Coletiva')).toBeInTheDocument()

  expect(await screen.findByText('Torneio A')).toBeInTheDocument()

  const user = userEvent.setup()
  await user.click(screen.getByRole('button', { name: 'Equipas' }))
  expect(await screen.findByText('Team A')).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Eliminar' }))
  expect(await screen.findByText('Eliminar modalidade')).toBeInTheDocument()

  const confirmButton = screen.getAllByRole('button', { name: 'Eliminar' }).pop()
  if (!confirmButton) throw new Error('Confirm button not found')

  await user.click(confirmButton)

  await waitFor(() => {
    expect(screen.queryByText('Futebol')).not.toBeInTheDocument()
  })

  expect(screen.getByRole('heading', { name: 'Modalidades (1)' })).toBeInTheDocument()
  expect(screen.getByText('Atletismo')).toBeInTheDocument()
})
