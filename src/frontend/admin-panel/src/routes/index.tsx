import { createBrowserRouter, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Common pages
import NotFound from '../pages/NotFound';
import Unauthorized from '../pages/Unauthorized';

// Geral admin pages
import DashboardGeral from '../pages/geral/DashboardGeral';
import Administradores from '../pages/geral/Administradores';
import AdminDetail from '../pages/geral/AdministradorDetail';
import Modalities from '../pages/geral/Modalidades';
import ModalityDetails from '../pages/geral/ModalidadeDetail';
import NucleoListPage from '../pages/geral/Nucleos';
import NucleoDetails from '../pages/geral/NucleoDetails';
import Cursos from '../pages/geral/Cursos';
import CursoDetail from '../pages/geral/CursoDetail';
import Regulamentos from '../pages/geral/Regulamentos';
import FormatosPontuacao from '../pages/geral/FormatosPontuacao';
import Torneios from '../pages/geral/Torneios';
import TorneioDetails from '../pages/geral/TorneioDetails';
import JogoDetails from '../pages/geral/JogoDetails';
import SociosGeral from '../pages/geral/Socios';

// Nucleo admin pages
import DashboardNucleo from '../pages/nucleo/DashboardNucleo';
import Membros from '../pages/nucleo/Membros';
import MemberDetail from '../pages/nucleo/MemberDetail';
import Equipas from '../pages/nucleo/Equipas';
import TeamDetailPage from '../pages/nucleo/TeamDetail';
import Jogos from '../pages/nucleo/Jogos';
import MatchDetailPage from '../pages/nucleo/MatchDetail';
import SociosNucleo from '../pages/nucleo/Socios';

// Components
import ProtectedRoute from '../components/ProtectedRoute';

/**
 * Post-login landing: redirect each authenticated user to their own
 * dashboard based on the Keycloak realm role they hold.
 */
const RootRedirect = () => {
  const { adminRole, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600" />
      </div>
    );
  }

  if (adminRole === 'general_admin') return <Navigate to="/geral/dashboard" replace />;
  if (adminRole === 'nucleo_admin') return <Navigate to="/nucleo/dashboard" replace />;
  return <Navigate to="/unauthorized" replace />;
};

export const router = createBrowserRouter([
  // ============================================
  // Root redirect (Keycloak handles login itself)
  // ============================================
  {
    path: '/',
    element: <RootRedirect />,
  },
  {
    path: '/unauthorized',
    element: <Unauthorized />,
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
    element: <ProtectedRoute requiredRole="geral"><NucleoListPage /></ProtectedRoute>,
  },
  {
    path: '/geral/nucleos/:id',
    element: <ProtectedRoute requiredRole="geral"><NucleoDetails /></ProtectedRoute>,
  },
  {
    path: '/geral/cursos',
    element: <ProtectedRoute requiredRole="geral"><Cursos /></ProtectedRoute>,
  },
  {
    path: '/geral/cursos/:id',
    element: <ProtectedRoute requiredRole="geral"><CursoDetail /></ProtectedRoute>,
  },
  {
    path: '/geral/regulamentos',
    element: <ProtectedRoute requiredRole="geral"><Regulamentos /></ProtectedRoute>,
  },
  {
    path: '/geral/formatos-prova',
    element: <ProtectedRoute requiredRole="geral"><FormatosPontuacao /></ProtectedRoute>,
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
  {
    path: '/geral/socios',
    element: <ProtectedRoute requiredRole="geral"><SociosGeral /></ProtectedRoute>,
  },

  // ============================================
  // Nucleo Admin Routes
  // ============================================
  {
    path: '/nucleo/dashboard',
    element: <ProtectedRoute requiredRole="nucleo"><DashboardNucleo /></ProtectedRoute>,
  },
  {
    path: '/nucleo/socios',
    element: <ProtectedRoute requiredRole="geral"><SociosNucleo /></ProtectedRoute>,
  },
  {
    path: '/nucleo/membros',
    element: <ProtectedRoute requiredRole="nucleo"><Membros /></ProtectedRoute>,
  },
  {
    path: '/nucleo/membros/:type/:id',
    element: <ProtectedRoute requiredRole="nucleo"><MemberDetail /></ProtectedRoute>,
  },
  {
    path: '/nucleo/equipas',
    element: <ProtectedRoute requiredRole="nucleo"><Equipas /></ProtectedRoute>,
  },
  {
    path: '/nucleo/equipas/:id',
    element: <ProtectedRoute requiredRole="nucleo"><TeamDetailPage /></ProtectedRoute>,
  },
  {
    path: '/nucleo/jogos',
    element: <ProtectedRoute requiredRole="nucleo"><Jogos /></ProtectedRoute>,
  },
  {
    path: '/nucleo/jogos/:id',
    element: <ProtectedRoute requiredRole="nucleo"><MatchDetailPage /></ProtectedRoute>,
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
