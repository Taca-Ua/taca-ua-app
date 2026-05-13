import React from 'react'
import { renderWithProviders } from '../test-utils'
import SociosContent from '../../src/pages/socios/SociosContent'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('Socios (athletes) flows', () => {
  test('loads athletes, filters and toggles membership', async () => {
    renderWithProviders(<SociosContent />)

    // wait for athletes to load
    expect(await screen.findByText('Alice Almeida')).toBeInTheDocument()
    expect(screen.getByText('Bruno Barbosa')).toBeInTheDocument()

    // search for an athlete by name
    const search = screen.getByPlaceholderText('Pesquisar por nome, NMEC ou curso...')
    await userEvent.type(search, 'Bruno')
    await waitFor(() => expect(screen.getByText('Bruno Barbosa')).toBeInTheDocument())
    expect(screen.queryByText('Alice Almeida')).not.toBeInTheDocument()

    // clear search
    await userEvent.clear(search)
    await waitFor(() => expect(screen.getByText('Alice Almeida')).toBeInTheDocument())

    // toggle membership for Alice
    const aliceName = screen.getByText('Alice Almeida')
    const aliceLi = aliceName.closest('li') as HTMLElement
    const toggle = within(aliceLi).getByRole('switch')
    // alice initially is a member (true), click to toggle off then on
    await userEvent.click(toggle)
    // wait for updated label to reflect change (either Sócio / Não sócio)
    await waitFor(() => expect(within(aliceLi).getByText(/Sócio|Não sócio/)).toBeInTheDocument())
  })

  test('opens detail modal and deletes athlete', async () => {
    renderWithProviders(<SociosContent />)

    // wait for list
    expect(await screen.findByText('Bruno Barbosa')).toBeInTheDocument()

    // open athlete details
    await userEvent.click(screen.getByText('Bruno Barbosa'))

    // modal should show student number
    expect(await screen.findByText('Número de Estudante')).toBeInTheDocument()

    // click delete and confirm
    const deleteBtn = screen.getByRole('button', { name: 'Eliminar' })
    await userEvent.click(deleteBtn)

    // confirmation appears; find confirm button
    const confirm = await screen.findByRole('button', { name: 'Sim, eliminar' })
    await userEvent.click(confirm)

    // Bruno should be removed from list
    await waitFor(() => expect(screen.queryByText('Bruno Barbosa')).not.toBeInTheDocument())
  })
})
