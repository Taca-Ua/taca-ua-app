import { createBrowserRouter } from 'react-router-dom';
import Home from '../pages/Home';
import NotFound from '../pages/NotFound';
import Regulamentos from '../pages/Regulamentos';
import Calendario from '../pages/Calendario';
import MatchDetailPage from '../pages/MatchDetail';
import TeamDetailPage from '../pages/TeamDetail';
import Tournaments from '../pages/classificacao/Tournaments';
import TournamentDetailPage from '../pages/classificacao/TournamentDetail';
import GeneralRankingPage from '../pages/classificacao/GeneralRanking';
import ModalityRankingPage from '../pages/classificacao/ModalityRanking';
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
    path: '/jogos/:id',
    element: <MatchDetailPage />
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
    path: '/ranking',
    element: <GeneralRankingPage />
  },
  {
    path: '/ranking/modalidade',
    element: <ModalityRankingPage />
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
    path: '/equipas/:id',
    element: <TeamDetailPage />
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
