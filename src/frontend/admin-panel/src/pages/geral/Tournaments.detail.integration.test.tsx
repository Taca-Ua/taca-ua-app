import { fireEvent, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { expect, vi } from 'vitest'
import Torneios from './Tournaments'
import TorneioDetails from './TorneioDetails'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

test('opens a tournament detail page and activates a draft tournament', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/torneios" element={<Torneios />} />
      <Route path="/torneios/:id" element={<TorneioDetails />} />
    </Routes>,
    { initialEntries: ['/torneios'] },
  )

  const user = userEvent.setup()

  // Wait for tournaments to load
  expect(await screen.findByText('Torneio A')).toBeInTheDocument()
  expect(screen.getByText('Torneio B')).toBeInTheDocument()

  // Open Torneio B details
  await user.click(screen.getByText('Torneio B'))

  // Wait for tournament details to load
  expect(await screen.findByRole('heading', { name: 'Detalhes do Torneio' })).toBeInTheDocument()
  expect(await screen.findByText('Torneio B')).toBeInTheDocument()
  expect(screen.getByText('Rascunho')).toBeInTheDocument()

  // Activate the tournament
  await user.click(screen.getByRole('button', { name: 'Ativar Torneio' }))
  const confirmButton = await screen.findByRole('button', { name: 'Ativar' })
  await user.click(confirmButton)

  // Wait for status to update to "Ativo"
  await waitFor(() => {
    expect(screen.getByText('Ativo')).toBeInTheDocument()
  })
})

test('finishes an active tournament after assigning final positions', async () => {
  const { container } = renderWithProviders(
    <Routes>
      <Route path="/torneios" element={<Torneios />} />
      <Route path="/torneios/:id" element={<TorneioDetails />} />
    </Routes>,
    { initialEntries: ['/torneios/t1'] },
  )

  const user = userEvent.setup()

  // Wait for tournament details to load
  expect(await screen.findByRole('heading', { name: 'Detalhes do Torneio' })).toBeInTheDocument()
  expect(screen.getByText('Torneio A')).toBeInTheDocument()
  expect(screen.getByText('Ativo')).toBeInTheDocument()

  // Open finalize tournament modal
  await user.click(screen.getByRole('button', { name: 'Finalizar Torneio' }))
  expect(await screen.findByRole('heading', { name: 'Finalizar Torneio - Classificação Final' })).toBeInTheDocument()

  // Simulate drag and drop to assign final positions
  const dragAndDrop = (source: HTMLElement, target: HTMLElement) => {
    const dataTransfer = {
      data: {} as Record<string, string>,
      dropEffect: 'move',
      effectAllowed: 'all',
      files: [],
      items: [],
      types: [],
      setData(format: string, value: string) {
        this.data[format] = value
      },
      getData(format: string) {
        return this.data[format] || ''
      },
      clearData() {
        this.data = {}
      },
    } as unknown as DataTransfer

    fireEvent.dragStart(source, { dataTransfer })
    fireEvent.dragEnter(target, { dataTransfer })
    fireEvent.dragOver(target, { dataTransfer })
    fireEvent.drop(target, { dataTransfer })
    fireEvent.dragEnd(source, { dataTransfer })
  }

  const firstCompetitor = container.querySelector('[data-rfd-draggable-id="comp-1"]') as HTMLElement | null
  const secondCompetitor = container.querySelector('[data-rfd-draggable-id="comp-2"]') as HTMLElement | null
  const firstPosition = container.querySelector('[data-rfd-droppable-id="1"]') as HTMLElement | null

  if (!firstCompetitor || !secondCompetitor || !firstPosition) {
    throw new Error('Tournament finish drag targets not found')
  }

  // Assign first competitor to 1st place and second competitor to 2nd place
  dragAndDrop(firstCompetitor, firstPosition)
  dragAndDrop(secondCompetitor, firstPosition)

  // Finalize the tournament
  const finishModalButton = screen.getAllByRole('button', { name: 'Finalizar Torneio' }).pop()
  if (!finishModalButton) throw new Error('Finish modal button not found')
  await user.click(finishModalButton)

  // Wait for status to update to "Finalizado"
  await waitFor(() => {
    expect(screen.getByText('Finalizado')).toBeInTheDocument()
  })
})
