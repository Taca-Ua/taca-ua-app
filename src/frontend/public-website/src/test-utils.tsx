import type { ReactElement } from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

type RenderOptions = {
  initialEntries?: string[]
}

export function renderWithRouter(
  ui: ReactElement,
  { initialEntries = ['/'] }: RenderOptions = {},
) {
  return render(
    <BrowserRouter>
      {ui}
    </BrowserRouter>,
  )
}
