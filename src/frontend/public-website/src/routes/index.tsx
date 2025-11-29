import { createBrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import NotFound from '../pages/NotFound';
import Geral from '../pages/classificacao/Geral';
import Modalidade from '../pages/classificacao/Modalidade';
import TorneioDetail from '../pages/classificacao/TorneioDetail';
import Regulamentos from '../pages/Regulamentos';
import Calendario from '../pages/Calendario';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />
  },
  {
    path: '/classificacao/geral',
    element: <Geral />
  },
  {
    path: '/classificacao/modalidade',
    element: <Modalidade />
  },
  {
    path: '/classificacao/torneio/:id',
    element: <TorneioDetail />
  },
  {
    path: '/calendario',
    element: <Calendario />
  },
  {
    path: '/regulamentos',
    element: <Regulamentos />
  },
  {
    path: '*',
    element: <NotFound />
  },
]);
