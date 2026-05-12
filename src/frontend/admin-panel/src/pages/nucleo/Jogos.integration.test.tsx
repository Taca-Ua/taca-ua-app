import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import Jogos from './Jogos'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

test('loads matches and filters by status', async () => {
  renderWithProviders(<Jogos />)
  const user = userEvent.setup()

  // Wait for matches to load
  expect(await screen.findByText('Team A vs Team B')).toBeInTheDocument()
  expect(screen.getByText('Torneio A')).toBeInTheDocument()
  expect(screen.getByText('Pavilhão A')).toBeInTheDocument()

  expect(screen.getAllByText('Agendado').length).toBeGreaterThan(0)

  // Filter by status
  await user.selectOptions(screen.getByRole('combobox'), 'finished')
  expect(await screen.findByText('Nenhum jogo encontrado.')).toBeInTheDocument()
})

test('switches to calendar view and shows no games on today', async () => {
  renderWithProviders(<Jogos />)
  const user = userEvent.setup()

  // ensure initial load
  expect(await screen.findByText('Team A vs Team B')).toBeInTheDocument()

  // switch to calendar view
  await user.click(screen.getByRole('button', { name: 'Calendário' }))

  // the default selected day is today; our sample match is on a different day
  expect(await screen.findByText('Não há jogos neste dia.')).toBeInTheDocument()
})
