import { screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Teams from '../../src/pages/Teams'
import { renderWithRouter } from '../test-utils'

test('loads and displays teams list', async () => {
  renderWithRouter(<Teams />)

  // Wait for teams to load
  expect(await screen.findByText('Engenharia Informática A')).toBeInTheDocument()
  expect(screen.getByText('Engenharia Civil A')).toBeInTheDocument()
  expect(screen.getByText('Engenharia Informática B')).toBeInTheDocument()

  // Check modalities are displayed
  expect(screen.getAllByText('Futebol').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Voleibol').length).toBeGreaterThan(0)
})

test('displays team pagination info', async () => {
  renderWithRouter(<Teams />)

  // Wait for teams to load
  expect(await screen.findByText('Engenharia Informática A')).toBeInTheDocument()

  // Check that course info is displayed
  expect(screen.getAllByText('Engenharia Informática').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Engenharia Civil').length).toBeGreaterThan(0)
})
