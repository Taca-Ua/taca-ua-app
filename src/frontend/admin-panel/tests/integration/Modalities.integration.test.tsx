import { screen } from '@testing-library/react'
import Modalities from '../../src/pages/geral/Modalities'
import { renderWithProviders } from '../test-utils'

test('loads modalities and shows the available filter options', async () => {
  renderWithProviders(<Modalities />)

  expect(await screen.findByText('Futebol')).toBeInTheDocument()
  expect(await screen.findByText('Atletismo')).toBeInTheDocument()

  expect(screen.getByRole('button', { name: '+ Adicionar Modalidade' })).toBeEnabled()
  expect(screen.getByRole('heading', { name: /Modalidades \(2\)/i })).toBeInTheDocument()
  expect(screen.getByRole('option', { name: 'Coletiva' })).toBeInTheDocument()
  expect(screen.getByRole('option', { name: 'Individual' })).toBeInTheDocument()
})
