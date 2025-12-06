import { createBrowserRouter } from 'react-router-dom';

// Common pages
import Login from '../pages/Login';
import NotFound from '../pages/NotFound';

// Geral admin pages
import LoginGeral from '../pages/geral/LoginGeral';
import DashboardGeral from '../pages/geral/DashboardGeral';
import Administradores from '../pages/geral/Administradores';
import AdminDetail from '../pages/geral/AdministradorDetail';
import Modalities from '../pages/geral/Modalidades';
import ModalityDetails from '../pages/geral/ModalidadeDetail';
import Nucleo from '../pages/geral/Nucleos';
import NucleoDetails from '../pages/geral/NucleoDetails';
import Regulamentos from '../pages/geral/Regulamentos';
import Torneios from '../pages/geral/Torneios';
import TorneioDetails from '../pages/geral/TorneioDetails';
import JogoDetails from '../pages/geral/JogoDetails';

// Nucleo admin pages
import LoginNucleo from '../pages/nucleo/LoginNucleo';
import DashboardNucleo from '../pages/nucleo/DashboardNucleo';
import Membros from '../pages/nucleo/Membros';
import MemberDetail from '../pages/nucleo/MemberDetail';
import Equipas from '../pages/nucleo/Equipas';
import TeamDetail from '../pages/nucleo/TeamDetail';
import Jogos from '../pages/nucleo/Jogos';
import MatchDetail from '../pages/nucleo/MatchDetail';

// Components
import ProtectedRoute from '../components/ProtectedRoute';

export const router = createBrowserRouter([
  // ============================================
  // Authentication Routes
  // ============================================
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
    path: '/login/nucleo',
    element: <LoginNucleo />,
  },

  // ============================================
  // Geral Admin Routes
  // ============================================
  {
    path: '/geral/dashboard',
    element: <ProtectedRoute requiredRole="geral"><DashboardGeral /></ProtectedRoute>,
  },
  {
    path: '/geral/administradores',
    element: <ProtectedRoute requiredRole="geral"><Administradores /></ProtectedRoute>,
  },
  {
    path: '/geral/administradores/:id',
    element: <ProtectedRoute requiredRole="geral"><AdminDetail /></ProtectedRoute>,
  },
  {
    path: '/geral/modalidades',
    element: <ProtectedRoute requiredRole="geral"><Modalities /></ProtectedRoute>,
  },
  {
    path: '/geral/modalidades/:id',
    element: <ProtectedRoute requiredRole="geral"><ModalityDetails /></ProtectedRoute>,
  },
  {
    path: '/geral/nucleos',
    element: <ProtectedRoute requiredRole="geral"><Nucleo /></ProtectedRoute>,
  },
  {
    path: '/geral/nucleos/:id',
    element: <ProtectedRoute requiredRole="geral"><NucleoDetails /></ProtectedRoute>,
  },
  {
    path: '/geral/regulamentos',
    element: <ProtectedRoute requiredRole="geral"><Regulamentos /></ProtectedRoute>,
  },
  {
    path: '/geral/torneios',
    element: <ProtectedRoute requiredRole="geral"><Torneios /></ProtectedRoute>,
  },
  {
    path: '/geral/torneios/:id',
    element: <ProtectedRoute requiredRole="geral"><TorneioDetails /></ProtectedRoute>,
  },
  {
    path: '/geral/jogos/:id',
    element: <ProtectedRoute requiredRole="geral"><JogoDetails /></ProtectedRoute>,
  },

  // ============================================
  // Nucleo Admin Routes
  // ============================================
  {
    path: '/nucleo/dashboard',
    element: <ProtectedRoute requiredRole="nucleo"><DashboardNucleo /></ProtectedRoute>,
  },
  {
    path: '/nucleo/membros',
    element: <ProtectedRoute requiredRole="nucleo"><Membros /></ProtectedRoute>,
  },
  {
    path: '/nucleo/membros/:id',
    element: <ProtectedRoute requiredRole="nucleo"><MemberDetail /></ProtectedRoute>,
  },
  {
    path: '/nucleo/equipas',
    element: <ProtectedRoute requiredRole="nucleo"><Equipas /></ProtectedRoute>,
  },
  {
    path: '/nucleo/equipas/:id',
    element: <ProtectedRoute requiredRole="nucleo"><TeamDetail /></ProtectedRoute>,
  },
  {
    path: '/nucleo/jogos',
    element: <ProtectedRoute requiredRole="nucleo"><Jogos /></ProtectedRoute>,
  },
  {
    path: '/nucleo/jogos/:id',
    element: <ProtectedRoute requiredRole="nucleo"><MatchDetail /></ProtectedRoute>,
  },

  // ============================================
  // Fallback Route
  // ============================================
  {
    path: '*',
    element: <NotFound />,
  },
], {
  basename: '/admin'
});
