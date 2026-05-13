import { renderWithProviders } from '../test-utils'
import SociosContent from '../../src/pages/socios/SociosContent'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('Socios (staff) flows', () => {
  test('loads staff and deletes a member', async () => {
    renderWithProviders(<SociosContent />)

    // switch to staff tab
    await userEvent.click(screen.getByRole('button', { name: 'Staff' }))

    // wait for staff to load
    expect(await screen.findByText('Diana Duarte')).toBeInTheDocument()
    expect(screen.getByText('Eduardo Esteves')).toBeInTheDocument()

    // open Diana details
    await userEvent.click(screen.getByText('Diana Duarte'))

    // modal shows staff number label
    expect(await screen.findByText('Número de Staff')).toBeInTheDocument()

    // delete Diana
    const deleteBtn = screen.getByRole('button', { name: 'Eliminar' })
    await userEvent.click(deleteBtn)

    const confirm = await screen.findByRole('button', { name: 'Sim, eliminar' })
    await userEvent.click(confirm)

    await waitFor(() => expect(screen.queryByText('Diana Duarte')).not.toBeInTheDocument())
  })

  test('edits a staff member name', async () => {
    renderWithProviders(<SociosContent />)

    // switch to staff tab
    await userEvent.click(screen.getByRole('button', { name: 'Staff' }))

    // wait for list
    expect(await screen.findByText('Eduardo Esteves')).toBeInTheDocument()

    // open Eduardo details
    await userEvent.click(screen.getByText('Eduardo Esteves'))

    // open edit modal
    const editBtn = await screen.findByRole('button', { name: 'Editar' })
    await userEvent.click(editBtn)

    // change name (use placeholder to locate input)
    const input = await screen.findByPlaceholderText('Digite o nome do membro')
    await userEvent.clear(input)
    await userEvent.type(input, 'Eduardo Silva')

    // save
    const save = screen.getByRole('button', { name: 'Guardar' })
    await userEvent.click(save)

    // updated name should appear in list
    await waitFor(() => expect(screen.getAllByText('Eduardo Silva')))
  })
})
