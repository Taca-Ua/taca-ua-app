import { createBrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import NotFound from '../pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />
  },
  {
    path: '/classificacaogeral',
    element: <Home />
  },
  {
    path: '/classificacaomodalidade',
    element: <Home />
  },
  {
    path: '/calendario',
    element: <Home />
  },
  {
    path: '/regulamentos',
    element: <Home />
  },
  {
    path: '*',
    element: <NotFound />
  },
]);
