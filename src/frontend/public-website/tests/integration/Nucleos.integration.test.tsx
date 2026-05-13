import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import Nucleos from '../../src/pages/Nucleos'
import { renderWithRouter } from '../test-utils'

test('loads nucleos and displays list', async () => {
  renderWithRouter(<Nucleos />)

  // Wait for nucleos to load
  expect(await screen.findByText('Núcleo de Engenharia Informática')).toBeInTheDocument()
  expect(screen.getByText('Núcleo de Engenharia Civil')).toBeInTheDocument()
  expect(screen.getByText('Núcleo de Engenharia Elétrica')).toBeInTheDocument()

  // Check abbreviations are displayed (getAllByText due to multiple occurrences)
  expect(screen.getAllByText('NEI').length).toBeGreaterThan(0)
  expect(screen.getAllByText('NEC').length).toBeGreaterThan(0)
  expect(screen.getAllByText('NEE').length).toBeGreaterThan(0)
})

test('filters nucleos by search text', async () => {
  renderWithRouter(<Nucleos />)
  const user = userEvent.setup()

  // Wait for nucleos to load
  expect(await screen.findByText('Núcleo de Engenharia Informática')).toBeInTheDocument()

  // Search for "Elétrica"
  const searchInput = screen.getByPlaceholderText('Pesquisar núcleo...')
  await user.type(searchInput, 'Elétrica')

  // Should only show Engenharia Elétrica
  expect(screen.getByText('Núcleo de Engenharia Elétrica')).toBeInTheDocument()
  expect(screen.queryByText('Núcleo de Engenharia Informática')).not.toBeInTheDocument()
  expect(screen.queryByText('Núcleo de Engenharia Civil')).not.toBeInTheDocument()
})

test('filters nucleos by abbreviation', async () => {
  renderWithRouter(<Nucleos />)
  const user = userEvent.setup()

  // Wait for nucleos to load
  expect(await screen.findByText('Núcleo de Engenharia Informática')).toBeInTheDocument()

  // Search for "NEC"
  const searchInput = screen.getByPlaceholderText('Pesquisar núcleo...')
  await user.type(searchInput, 'NEC')

  // Should only show Engenharia Civil
  expect(screen.getByText('Núcleo de Engenharia Civil')).toBeInTheDocument()
  expect(screen.queryByText('Núcleo de Engenharia Informática')).not.toBeInTheDocument()
  expect(screen.queryByText('Núcleo de Engenharia Elétrica')).not.toBeInTheDocument()
})
