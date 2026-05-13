import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { expect, test } from 'vitest'
import Equipas from '../../src/pages/nucleo/Teams'
import TeamDetailPage from '../../src/pages/nucleo/TeamDetail'
import { renderWithProviders } from '../test-utils'

test('loads teams and filters by modality and course', async () => {
  renderWithProviders(<Equipas />)
  const user = userEvent.setup()

  // Wait for teams to load
  expect(await screen.findByText('Team A')).toBeInTheDocument()
  expect(screen.getByText('Team B')).toBeInTheDocument()

  // Filter by modality
  await user.selectOptions(screen.getByLabelText('Modalidade'), 'mod-1')
  expect(screen.getByText('Team A')).toBeInTheDocument()
  expect(screen.queryByText('Team B')).not.toBeInTheDocument()

  // Filter by course
  await user.selectOptions(screen.getByLabelText('Curso'), 'c1')
  expect(screen.getByText('Team A')).toBeInTheDocument()

  await user.selectOptions(screen.getByLabelText('Modalidade'), '')
  await user.selectOptions(screen.getByLabelText('Curso'), 'c2')
  expect(await screen.findByText('Team B')).toBeInTheDocument()
  expect(screen.queryByText('Team A')).not.toBeInTheDocument()
})

test('opens team details and edits the team name', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/equipas/:id" element={<TeamDetailPage />} />
    </Routes>,
    { initialEntries: ['/equipas/team-2'] },
  )

  const user = userEvent.setup()

  // Wait for team details to load
  expect(await screen.findByRole('heading', { name: 'Detalhes da Equipa' })).toBeInTheDocument()
  expect(screen.getByText('Team B')).toBeInTheDocument()
  expect(screen.getByText('Atletismo')).toBeInTheDocument()

  // Edit the team name
  await user.click(screen.getByRole('button', { name: 'Editar' }))
  const nameInput = await screen.findByPlaceholderText('Digite o nome da equipa')
  await user.clear(nameInput)
  await user.type(nameInput, 'Team B Updated')
  await user.click(screen.getByRole('button', { name: 'Guardar' }))

// Wait for the updated team name to appear
  await waitFor(() => {
    expect(screen.getByText('Team B Updated')).toBeInTheDocument()
  })
})
