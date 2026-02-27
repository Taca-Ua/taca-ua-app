import { createBrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import NotFound from '../pages/NotFound';
import Regulamentos from '../pages/Regulamentos';
import Calendario from '../pages/Calendario';
import Tournaments from '../pages/classificacao/Tournaments';
import TournamentDetailPage from '../pages/classificacao/TournamentDetail';
import Students from '../pages/Students';
import Teams from '../pages/Teams';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />
  },
  {
    path: '/calendario',
    element: <Calendario />
  },
  {
    path: '/torneios',
    element: <Tournaments />
  },
  {
    path: '/torneios/:id',
    element: <TournamentDetailPage />
  },
  {
    path: '/estudantes',
    element: <Students />
  },
  {
    path: '/equipas',
    element: <Teams />
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
