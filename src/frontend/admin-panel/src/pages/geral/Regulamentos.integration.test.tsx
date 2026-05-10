import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import Regulamentos from './Regulamentos'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

test('loads regulations, filters by search, opens details modal, and removes regulation after delete confirmation', async () => {
  renderWithProviders(<Regulamentos />)

  // Initial load
  expect(await screen.findByRole('heading', { name: /Gest[aã]o de Regulamentos/i })).toBeInTheDocument()
  expect(await screen.findByText('Regulamento Geral')).toBeInTheDocument()
  expect(await screen.findByText('Guia de Arbitragem')).toBeInTheDocument()

  //Use filters to find specific regulation
  const searchInput = screen.getByPlaceholderText('Pesquisar regulamento...')
  await userEvent.type(searchInput, 'Arbitragem')
  expect(screen.getByText('Guia de Arbitragem')).toBeInTheDocument()
  expect(screen.queryByText('Regulamento Geral')).not.toBeInTheDocument()

  // Clear the filter
  await userEvent.clear(searchInput)
  expect(await screen.findByText('Regulamento Geral')).toBeInTheDocument()

  // Open regfulamento details
  await userEvent.click(screen.getByText('Regulamento Geral'))
  expect(await screen.findByText('Aceder ao Ficheiro')).toBeInTheDocument()

  // Delete regulamento
  await userEvent.click(screen.getByRole('button', { name: 'Eliminar Documento' }))
  expect(await screen.findByText('Eliminar regulamento')).toBeInTheDocument()

  // Confirm delete
  const confirmDelete = screen.getAllByRole('button', { name: 'Eliminar' }).pop()
  if (!confirmDelete) throw new Error('Confirm delete button not found')
  await userEvent.click(confirmDelete)

  // Wait for deletion to complete and check that the regulation is removed from the list
  await waitFor(() => {
    expect(screen.queryByText('Regulamento Geral')).not.toBeInTheDocument()
  })
  expect(screen.getByText('Guia de Arbitragem')).toBeInTheDocument()
})
