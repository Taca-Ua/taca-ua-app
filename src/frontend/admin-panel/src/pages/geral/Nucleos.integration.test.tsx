import { describe, it, expect, beforeEach } from 'vitest'
import { vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { renderWithProviders } from '../../test-utils'
import Nucleo from './Nucleos'
import NucleoDetails from './NucleoDetails'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

describe('Nucleos Integration Tests', () => {
  beforeEach(() => {
  })

  it('loads nucleos, filters by search, and displays correct items', async () => {
    const user = userEvent.setup()
    renderWithProviders(<Nucleo />, {
      initialEntries: ['/nucleos'],
    })

    // Wait for nucleos to load
    await waitFor(() => {
      expect(screen.getByText('NEECT')).toBeInTheDocument()
    })

    // Verify all three nucleos are displayed
    expect(screen.getByText('NEECT')).toBeInTheDocument()
    expect(screen.getByText('NES')).toBeInTheDocument()
    expect(screen.getByText('NEN')).toBeInTheDocument()

    // Verify full names are displayed
    expect(screen.getByText('Núcleo de Eletrônica e Computação')).toBeInTheDocument()
    expect(screen.getByText('Núcleo de Estruturas')).toBeInTheDocument()
    expect(screen.getByText('Núcleo de Energias')).toBeInTheDocument()

    // Test search filter - search for "Eletrônica"
    const searchInput = screen.getByPlaceholderText('Pesquisar núcleo...')
    await user.clear(searchInput)
    await user.type(searchInput, 'Eletrônica')

    // Verify only NEECT is displayed
    expect(screen.getByText('NEECT')).toBeInTheDocument()
    expect(screen.getByText('Núcleo de Eletrônica e Computação')).toBeInTheDocument()
    expect(screen.queryByText('Núcleo de Estruturas')).not.toBeInTheDocument()
    expect(screen.queryByText('Núcleo de Energias')).not.toBeInTheDocument()

    // Test search filter - search by abbreviation
    await user.clear(searchInput)
    await user.type(searchInput, 'NES')

    expect(screen.getByText('NES')).toBeInTheDocument()
    expect(screen.getByText('Núcleo de Estruturas')).toBeInTheDocument()
    expect(screen.queryByText('NEECT')).not.toBeInTheDocument()
    expect(screen.queryByText('NEN')).not.toBeInTheDocument()

    // Clear search to show all again
    await user.clear(searchInput)

    await waitFor(() => {
      expect(screen.getByText('NEECT')).toBeInTheDocument()
      expect(screen.getByText('NES')).toBeInTheDocument()
      expect(screen.getByText('NEN')).toBeInTheDocument()
    })
  })

  it('deletes a nucleo after confirming in modal and reflects change in list', async () => {
    const user = userEvent.setup()
    renderWithProviders(
      <Routes>
        <Route path="/nucleos/:id" element={<NucleoDetails />} />
        <Route path="/nucleos" element={<Nucleo />} />
      </Routes>,
      { initialEntries: ['/nucleos/nucleo-2'] },
    )

    // Wait for nucleo details to load
    expect(await screen.findByText('Núcleo de Estruturas')).toBeInTheDocument()
    expect(screen.getByText('NES')).toBeInTheDocument()

    // Verify associated courses are shown
    expect(screen.getByText('Mestrado Integrado em Engenharia Eletrónica')).toBeInTheDocument()
    expect(screen.getByText('Mestrado em Computação')).toBeInTheDocument()

    // Click the "Eliminar" button
    const deleteButtons = screen.getAllByRole('button', { name: /Eliminar/ })
    await user.click(deleteButtons[0])

    // Wait for confirmation modal and click confirm - use the last button (confirmation)
    const confirmDeleteButton = (await screen.findAllByRole('button', { name: /Eliminar/ })).pop()
    if (!confirmDeleteButton) throw new Error('Confirm delete button not found')
    await user.click(confirmDeleteButton)

    // Wait for navigation back to list and verify NES is removed
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Núcleos/ })).toBeInTheDocument()
    })

    expect(screen.queryByText('NES')).not.toBeInTheDocument()
    expect(screen.queryByText('Núcleo de Estruturas')).not.toBeInTheDocument()

    // Verify other nucleos still exist
    expect(screen.getByText('NEECT')).toBeInTheDocument()
    expect(screen.getByText('NEN')).toBeInTheDocument()
  })
})
