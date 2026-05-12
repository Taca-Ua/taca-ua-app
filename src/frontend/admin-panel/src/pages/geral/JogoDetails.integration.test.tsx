import { screen, within, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { expect, test, vi } from 'vitest'
import JogoDetails from './JogoDetails'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

test('loads match detail and shows participants and actions', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/jogos/:id" element={<JogoDetails />} />
      <Route path="/torneios/:id" element={<div>TORNEIO PAGE</div>} />
    </Routes>,
    { initialEntries: ['/jogos/match-1'] },
  )

  // Wait for match details to load
  expect(await screen.findByRole('heading', { name: 'Detalhes do Jogo' })).toBeInTheDocument()
  expect(screen.getAllByText('Team A').length).toBeGreaterThan(0)
  expect(screen.getAllByText('Team B').length).toBeGreaterThan(0)
  expect(screen.getByRole('button', { name: 'Baixar Ficha de Jogo' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Eliminar Jogo' })).toBeInTheDocument()
})

test('add and delete comment flow', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/jogos/:id" element={<JogoDetails />} />
    </Routes>,
    { initialEntries: ['/jogos/match-1'] },
  )

  const user = userEvent.setup()

  // wait for load
  expect(await screen.findByRole('heading', { name: 'Detalhes do Jogo' })).toBeInTheDocument()

  // add a comment
  const textarea = screen.getByPlaceholderText('Adicionar um comentário...')
  await user.type(textarea, 'Nice match')
  await user.click(screen.getByRole('button', { name: 'Adicionar Comentário' }))

  // comment should appear
  expect(await screen.findByText('Nice match')).toBeInTheDocument()

  // delete the comment
  const commentBlock = screen.getByText('Nice match').closest('div')
  const deleteBtn = within(commentBlock as HTMLElement).getByRole('button')
  await user.click(deleteBtn)

  // confirm modal appears with 'Eliminar' label
  await user.click(await screen.findByRole('button', { name: 'Eliminar' }))

  await waitFor(() => expect(screen.queryByText('Nice match')).not.toBeInTheDocument())
})

test('delete match navigates back to tournament page', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/jogos/:id" element={<JogoDetails />} />
      <Route path="/torneios/:id" element={<div>TORNEIO PAGE</div>} />
    </Routes>,
    { initialEntries: ['/jogos/match-1'] },
  )

  const user = userEvent.setup()

  // wait for load
  expect(await screen.findByRole('heading', { name: 'Detalhes do Jogo' })).toBeInTheDocument()

  // click delete and confirm
  await user.click(screen.getByRole('button', { name: 'Eliminar Jogo' }))
  await user.click(await screen.findByRole('button', { name: 'Sim, Eliminar' }))

  // Should navigate to tournament page
  expect(await screen.findByText('TORNEIO PAGE')).toBeInTheDocument()
})

test('publish results updates scores and status', async () => {
  renderWithProviders(
    <Routes>
      <Route path="/jogos/:id" element={<JogoDetails />} />
    </Routes>,
    { initialEntries: ['/jogos/match-1'] },
  )

  const user = userEvent.setup()
  expect(await screen.findByRole('heading', { name: 'Detalhes do Jogo' })).toBeInTheDocument()

  // open publish modal
  await user.click(screen.getByRole('button', { name: 'Publicar Resultados' }))

  // modal should appear (heading)
  expect(await screen.findByRole('heading', { name: 'Publicar Resultados' })).toBeInTheDocument()

  // find score inputs by placeholder
  const inputs = screen.getAllByPlaceholderText('Digite a pontuação')
  await user.clear(inputs[0])
  await user.type(inputs[0], '2')
  await user.clear(inputs[1])
  await user.type(inputs[1], '1')

  // click publish
  await user.click(screen.getByRole('button', { name: 'Publicar' }))

  // after publishing, scores should be visible in the results section
  expect(await screen.findByText('2')).toBeInTheDocument()
  expect(await screen.findByText('1')).toBeInTheDocument()

  // status badge should indicate finished (Terminado)
  expect(await screen.findByText('Terminado')).toBeInTheDocument()
})
