import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import Regulamentos from './Regulamentos'
import { renderWithRouter } from '../test-utils'

test('loads and displays regulations list', async () => {
  renderWithRouter(<Regulamentos />)

  // Wait for regulations to load
  expect(await screen.findByText('Regulamento de Futebol')).toBeInTheDocument()
  expect(screen.getByText('Regulamento de Voleibol')).toBeInTheDocument()
  expect(screen.getByText('Regulamento de Atletismo')).toBeInTheDocument()
})

test('filters regulations by search text', async () => {
  renderWithRouter(<Regulamentos />)
  const user = userEvent.setup()

  // Wait for regulations to load
  expect(await screen.findByText('Regulamento de Futebol')).toBeInTheDocument()

  // Search for "Voleibol"
  const searchInput = screen.getByPlaceholderText('Procurar...')
  await user.type(searchInput, 'Voleibol')

  // Should only show Voleibol
  expect(screen.getByText('Regulamento de Voleibol')).toBeInTheDocument()
  expect(screen.queryByText('Regulamento de Futebol')).not.toBeInTheDocument()
  expect(screen.queryByText('Regulamento de Atletismo')).not.toBeInTheDocument()
})

test('clears search to show all regulations', async () => {
  renderWithRouter(<Regulamentos />)
  const user = userEvent.setup()

  // Wait for regulations to load
  expect(await screen.findByText('Regulamento de Futebol')).toBeInTheDocument()

  // Search for "Atletismo"
  const searchInput = screen.getByPlaceholderText('Procurar...')
  await user.type(searchInput, 'Atletismo')
  expect(screen.queryByText('Regulamento de Futebol')).not.toBeInTheDocument()

  // Clear search
  await user.clear(searchInput)

  // All regulations should be visible again
  expect(screen.getByText('Regulamento de Futebol')).toBeInTheDocument()
  expect(screen.getByText('Regulamento de Voleibol')).toBeInTheDocument()
  expect(screen.getByText('Regulamento de Atletismo')).toBeInTheDocument()
})
