import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test } from 'vitest'
import Calendario from '../../src/pages/Calendario'
import { renderWithRouter } from '../test-utils'

test('renders Calendario component and switches to list view', async () => {
  renderWithRouter(<Calendario />)
  const user = userEvent.setup()

  // Wait for the heading to appear
  expect(await screen.findByText('Calendário de Jogos')).toBeInTheDocument()

  // Verify view toggle buttons exist
  const listBtn = screen.getByRole('button', { name: /lista/i })
  expect(listBtn).toBeInTheDocument()

  // Switch to list view
  await user.click(listBtn)

  // In list view, we expect to see match locations
  expect(await screen.findByText('Pavilhão A')).toBeInTheDocument()
})

test('displays matches in list view with proper information', async () => {
  renderWithRouter(<Calendario />)
  const user = userEvent.setup()

  // Wait for the heading to appear
  expect(await screen.findByText('Calendário de Jogos')).toBeInTheDocument()

  // Switch to list view
  const listBtn = screen.getByRole('button', { name: /lista/i })
  await user.click(listBtn)

  // Check for specific match information
  expect(await screen.findByText('Pavilhão A')).toBeInTheDocument()
  expect(screen.getByText('Pavilhão B')).toBeInTheDocument()
  expect(screen.getByText('Campo A')).toBeInTheDocument()
})

test('has functional calendar and list view toggle', async () => {
  renderWithRouter(<Calendario />)
  const user = userEvent.setup()

  // Wait for heading
  expect(await screen.findByText('Calendário de Jogos')).toBeInTheDocument()

  // Find both buttons
  const listBtn = screen.getByRole('button', { name: /lista/i })
  const calendarBtn = screen.getByRole('button', { name: /calendário/i })

  // Both buttons should exist
  expect(listBtn).toBeInTheDocument()
  expect(calendarBtn).toBeInTheDocument()

  // Click list button
  await user.click(listBtn)
  // Should see a location (proves list view is active)
  expect(await screen.findByText('Pavilhão A')).toBeInTheDocument()

  // Click calendar button
  await user.click(calendarBtn)
  // Should still be able to find the header
  expect(screen.getByText('Calendário de Jogos')).toBeInTheDocument()
})
