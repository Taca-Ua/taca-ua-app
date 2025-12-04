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
import ProtectedRoute from '../components/ProtectedRoute';

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
    path: '/nucleo/dashboard',
    element: <ProtectedRoute><DashboardNucleo /></ProtectedRoute>,
  },
  {
    path: '/nucleo/membros',
    element: <ProtectedRoute><Membros /></ProtectedRoute>,
  },
  {
    path: '/nucleo/membros/:id',
    element: <ProtectedRoute><MemberDetail /></ProtectedRoute>,
  },
  {
    path: '/nucleo/equipas',
    element: <ProtectedRoute><Equipas /></ProtectedRoute>,
  },
  {
    path: '/nucleo/equipas/:id',
    element: <ProtectedRoute><TeamDetail /></ProtectedRoute>,
  },
  {
    path: '/nucleo/jogos',
    element: <ProtectedRoute><Jogos /></ProtectedRoute>,
  },
  {
    path: '/nucleo/jogos/:id',
    element: <ProtectedRoute><MatchDetail /></ProtectedRoute>,
  },
  {
    path: '*',
    element: <NotFound />,
  },
], {
  basename: '/admin'
});
