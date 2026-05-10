import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { expect, it, vi } from 'vitest'
import Cursos from './Courses'
import CursoDetail from './CourseDetail'
import { renderWithProviders } from '../../test-utils'

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({ isAdminGeneral: true }),
}))

describe('Cursos Integration Tests', () => {
  it('loads courses, filters by search and nucleo, and keeps the list sorted', async () => {
    const user = userEvent.setup()

    renderWithProviders(<Cursos />, {
      initialEntries: ['/cursos'],
    })

    // Wait for courses to load
    expect(await screen.findByRole('heading', { name: 'Cursos' })).toBeInTheDocument()
    expect(screen.getAllByText('LEC')).toHaveLength(2)
    expect(screen.getAllByText('LEI')).toHaveLength(2)
    expect(screen.getAllByText('MA')).toHaveLength(2)

    // Use filters to find specific courses
    const searchInput = screen.getByPlaceholderText('Pesquisar curso...')
    await user.type(searchInput, 'Engenharia')

    expect(screen.getByText('Engenharia Civil')).toBeInTheDocument()
    expect(screen.getByText('Engenharia Informática')).toBeInTheDocument()
    expect(screen.queryByText('Matemática Aplicada')).not.toBeInTheDocument()

    //
    const nucleoSelect = screen.getByRole('combobox')
    await user.selectOptions(nucleoSelect, 'nucleo-2')

    expect(screen.getByText('Engenharia Civil')).toBeInTheDocument()
    expect(screen.queryByText('Engenharia Informática')).not.toBeInTheDocument()
    expect(screen.queryByText('Matemática Aplicada')).not.toBeInTheDocument()

    await user.clear(searchInput)
    await user.selectOptions(nucleoSelect, '')

    await waitFor(() => {
      expect(screen.getByText('Engenharia Civil')).toBeInTheDocument()
      expect(screen.getByText('Engenharia Informática')).toBeInTheDocument()
      expect(screen.getByText('Matemática Aplicada')).toBeInTheDocument()
    })
  })

  it('edits a course and reflects the updated data after returning to the list', async () => {
    const user = userEvent.setup()

    renderWithProviders(
      <Routes>
        <Route path="/cursos/:id" element={<CursoDetail />} />
        <Route path="/cursos" element={<Cursos />} />
      </Routes>,
      { initialEntries: ['/cursos/course-1'] },
    )

    // Wait for course details to load
    expect(await screen.findByText('Engenharia Informática')).toBeInTheDocument()
    expect(screen.getAllByText('LEI')).toHaveLength(2)
    expect(screen.getByText('Núcleo de Eletrónica e Computação')).toBeInTheDocument()

    // Click the "Editar" button
    await user.click(screen.getByRole('button', { name: 'Editar' }))
    expect(await screen.findByRole('heading', { name: 'Editar Curso' })).toBeInTheDocument()

    const nameInput = screen.getByPlaceholderText('Digite o nome do curso')
    const abbreviationInput = screen.getByPlaceholderText('Ex: MECT, LEI, LECI')

    // Update course name and abbreviation
    await user.clear(nameInput)
    await user.type(nameInput, 'Engenharia Informática Atualizada')
    await user.clear(abbreviationInput)
    await user.type(abbreviationInput, 'LIA')
    await user.click(screen.getByRole('button', { name: 'Salvar' }))

    // Wait for edit modal to close and details to update
    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: 'Editar Curso' })).not.toBeInTheDocument()
    })

    expect(screen.getByText('Engenharia Informática Atualizada')).toBeInTheDocument()
    expect(screen.getAllByText('LIA')).toHaveLength(2)

    await user.click(screen.getByRole('button', { name: 'Voltar' }))

    expect(await screen.findByRole('heading', { name: 'Cursos' })).toBeInTheDocument()
    expect(screen.getByText('Engenharia Informática Atualizada')).toBeInTheDocument()
    expect(screen.getAllByText('LIA')).toHaveLength(2)
    expect(screen.queryByText('Engenharia Informática')).not.toBeInTheDocument()
    expect(screen.queryAllByText('LEI')).toHaveLength(0)
  })

  it('deletes a course after confirming the modal and returns to the updated list', async () => {
    const user = userEvent.setup()

    renderWithProviders(
      <Routes>
        <Route path="/cursos/:id" element={<CursoDetail />} />
        <Route path="/cursos" element={<Cursos />} />
      </Routes>,
      { initialEntries: ['/cursos/course-2'] },
    )
    // Wait for course details to load
    expect(await screen.findByText('Engenharia Civil')).toBeInTheDocument()
    expect(screen.getAllByText('LEC')).toHaveLength(2)

    // CLick the "Eliminar" button
    await user.click(screen.getByRole('button', { name: 'Eliminar' }))

    // Confirm delete in modal
    const confirmDeleteButton = (await screen.findAllByRole('button', { name: 'Eliminar' })).pop()
    if (!confirmDeleteButton) throw new Error('Confirm delete button not found')

    await user.click(confirmDeleteButton)

    // Wait for navigation back to list and verify course is removed
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Cursos' })).toBeInTheDocument()
    })

    expect(screen.queryByText('Engenharia Civil')).not.toBeInTheDocument()
    expect(screen.queryByText('LEC')).not.toBeInTheDocument()
    expect(screen.getByText('Engenharia Informática')).toBeInTheDocument()
    expect(screen.getByText('Matemática Aplicada')).toBeInTheDocument()
  })
})
