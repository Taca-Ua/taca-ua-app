import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Tournaments from './Tournaments'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

test('loads tournaments, filters the list, and creates a new tournament', async () => {
  renderWithProviders(<Tournaments />)
  const user = userEvent.setup()

  // Wait for tournaments to load
  expect(await screen.findByText('Torneio A')).toBeInTheDocument()
  expect(screen.getByText('Torneio B')).toBeInTheDocument()

  // Test search filter - search for "Torneio B"
  const searchInput = screen.getByPlaceholderText('Pesquisar torneio...')
  await user.type(searchInput, 'Torneio B')

  // Verify only Torneio B is displayed
  expect(screen.getByText('Torneio B')).toBeInTheDocument()
  expect(screen.queryByText('Torneio A')).not.toBeInTheDocument()

  // Clear search to show all again
  await user.clear(searchInput)
  expect(await screen.findByText('Torneio A')).toBeInTheDocument()

  // Create a new tournament
  await user.click(screen.getByRole('button', { name: '+ Criar Torneio' }))
  expect(await screen.findByRole('heading', { name: 'Criar Torneio' })).toBeInTheDocument()

  // Fill out the create tournament form
  const createModal = screen.getByRole('heading', { name: 'Criar Torneio' }).closest('div')?.parentElement
  if (!createModal) throw new Error('Create modal not found')
  const nameInput = within(createModal).getByRole('textbox')
  await user.type(nameInput, 'Torneio Copa 2026')
  await user.click(screen.getByText('Selecionar Elemento'))
  const modalityOption = screen.getAllByText('Futebol').pop()
  if (!modalityOption) throw new Error('Modality option not found')
  await user.click(modalityOption)

  // Submit the form
  await user.click(screen.getByRole('button', { name: 'Criar' }))

  // Wait for the new tournament to appear in the list
  await waitFor(() => {
    expect(screen.getByText('Torneio Copa 2026')).toBeInTheDocument()
  })
})
