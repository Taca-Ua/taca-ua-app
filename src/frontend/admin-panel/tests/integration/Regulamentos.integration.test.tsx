import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect } from 'vitest'
import Regulamentos from '../../src/pages/geral/Regulamentos'
import { renderWithProviders } from '../test-utils'

test('loads regulations, filters by search, opens details modal, and removes regulation after delete confirmation', async () => {
  renderWithProviders(<Regulamentos />)
  const user = userEvent.setup()

  // Initial load
  expect(await screen.findByRole('heading', { name: /Gest[aã]o de Regulamentos/i })).toBeInTheDocument()
  expect(await screen.findByText('Regulamento Geral')).toBeInTheDocument()
  expect(await screen.findByText('Guia de Arbitragem')).toBeInTheDocument()

  //Use filters to find specific regulation
  const searchInput = screen.getByPlaceholderText('Pesquisar regulamento...')
  await user.type(searchInput, 'Arbitragem')
  expect(screen.getByText('Guia de Arbitragem')).toBeInTheDocument()
  expect(screen.queryByText('Regulamento Geral')).not.toBeInTheDocument()

  // Clear the filter
  await user.clear(searchInput)
  expect(await screen.findByText('Regulamento Geral')).toBeInTheDocument()

  // Open regfulamento details
  await user.click(screen.getByText('Regulamento Geral'))
  expect(await screen.findByText('Aceder ao Ficheiro')).toBeInTheDocument()

  // Delete regulamento
  await user.click(screen.getByRole('button', { name: 'Eliminar Documento' }))
  expect(await screen.findByText('Eliminar regulamento')).toBeInTheDocument()

  // Confirm delete
  const confirmDelete = screen.getAllByRole('button', { name: 'Eliminar' }).pop()
  if (!confirmDelete) throw new Error('Confirm delete button not found')
  await user.click(confirmDelete)

  // Wait for deletion to complete and check that the regulation is removed from the list
  await waitFor(() => {
    expect(screen.queryByText('Regulamento Geral')).not.toBeInTheDocument()
  })
  expect(screen.getByText('Guia de Arbitragem')).toBeInTheDocument()
})

test('edits a regulation and reflects the updated title in the regulations list', async () => {
  renderWithProviders(<Regulamentos />)
  const user = userEvent.setup()

  expect(await screen.findByText('Regulamento Geral')).toBeInTheDocument()

  // Open details modal
  await user.click(screen.getByText('Regulamento Geral'))
  expect(await screen.findByText('Aceder ao Ficheiro')).toBeInTheDocument()

  // Open edit modal
  await user.click(screen.getByRole('button', { name: 'Editar Documento' }))
  expect(await screen.findByRole('heading', { name: 'Editar Regulamento' })).toBeInTheDocument()

  // Update title and save
  const titleInput = screen.getByPlaceholderText('Ex: Regulamento de Basquetebol 2026')
  await user.clear(titleInput)
  await user.type(titleInput, 'Regulamento Geral Atualizado')
  await user.click(screen.getByRole('button', { name: 'Editar Regulamento' }))

  // Edit modal closes and list reflects new title
  await waitFor(() => {
    expect(screen.queryByRole('heading', { name: 'Editar Regulamento' })).not.toBeInTheDocument()
  })

  // Close details modal and assert list state only
  await user.click(screen.getByRole('button', { name: 'Fechar' }))
  expect(await screen.findByRole('heading', { name: /Gest[aã]o de Regulamentos/i })).toBeInTheDocument()
  expect(screen.getByText('Regulamento Geral Atualizado')).toBeInTheDocument()
  expect(screen.queryByText('Regulamento Geral')).not.toBeInTheDocument()
})
