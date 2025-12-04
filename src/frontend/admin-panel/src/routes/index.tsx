import { createBrowserRouter } from 'react-router-dom';
import DashboardNucleo from '../pages/nucleo/DashboardNucleo';
import Membros from '../pages/nucleo/Membros';
import MemberDetail from '../pages/nucleo/MemberDetail';
import Equipas from '../pages/nucleo/Equipas';
import TeamDetail from '../pages/nucleo/TeamDetail';
import Jogos from '../pages/nucleo/Jogos';
import MatchDetail from '../pages/nucleo/MatchDetail';
import NotFound from '../pages/NotFound';
import Login from '../pages/Login';
import LoginGeral from '../pages/geral/LoginGeral';
import LoginNucleo from '../pages/nucleo/LoginNucleo';
import DashboardGeral from '../pages/geral/DashboardGeral';
import Administradores from '../pages/geral/Administradores';
import AdminDetail from '../pages/geral/AdministradorDetail';
import Modalities from '../pages/geral/Modalidades';
import ModalityDetails from '../pages/geral/ModalityDetails';
import Regulamentos from '../pages/geral/Regulamentos';
import RegulamentoDetails from '../pages/geral/RegulamentoDetails';
import Torneios from '../pages/geral/Torneios';
import TorneioDetails from '../pages/geral/TorneioDetails';
import Nucleo from '../pages/geral/Nucleos';
import NucleoDetails from '../pages/geral/NucleoDetails';


export const router = createBrowserRouter([
  {
    path: '/',
    element: <Login />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/login/geral',
    element: <LoginGeral />,
  },
  {
    path: '/geral/dashboard',
    element: <DashboardGeral />,
  },
  {
    path: '/login/nucleo',
    element: <LoginNucleo />,
  },
  {
    path: '/geral/administradores',
    element: <Administradores />,
  },
  {
    path: '/geral/administradores/:id',
    element: <AdminDetail />,
  },
  {
    path: '/geral/modalidades',
    element: <Modalities />,
  },
  {
    path: '/geral/modalidades/:id',
    element: <ModalityDetails />,
  },
  {
    path: '/geral/regulamentos',
    element: <Regulamentos />,
  },
  {
    path: '/geral/regulamentos/:id',
    element: <RegulamentoDetails />,
  },
  {
    path: '/geral/nucleos',
    element: <Nucleo />,
  },
  {
    path: '/geral/nucleos/:id',
    element: <NucleoDetails />,
  },
  {
    path: '/nucleo/dashboard',
    element: <DashboardNucleo />,
  },
  {
    path: '/geral/torneios',
    element: <Torneios />,
  },
  {
    path: '/geral/torneios/:id',
    element: <TorneioDetails />,
  },
  {
    path: '/nucleo/membros',
    element: <Membros />,
  },
  {
    path: '/nucleo/membros/:id',
    element: <MemberDetail />,
  },
  {
    path: '/nucleo/equipas',
    element: <Equipas />,
  },
  {
    path: '/nucleo/equipas/:id',
    element: <TeamDetail />,
  },
  {
    path: '/nucleo/jogos',
    element: <Jogos />,
  },
  {
    path: '/nucleo/jogos/:id',
    element: <MatchDetail />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
], {
  basename: '/admin'
});
