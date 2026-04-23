import { createBrowserRouter, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import DashboardLayout from '../layouts/DashboardLayout';

// Common pages
import NotFound from '../pages/NotFound';
import Unauthorized from '../pages/Unauthorized';
import Dashboard from '../pages/Dashboard';

// Geral admin pages
import Administradores from '../pages/geral/Administradores';
import AdminDetailPage from '../pages/geral/AdministradorDetail.js';
import Modalities from '../pages/geral/Modalities';
import ModalityDetails from '../pages/geral/ModalityDetail';
import NucleoListPage from '../pages/geral/Nucleos';
import NucleoDetails from '../pages/geral/NucleoDetails';
import Cursos from '../pages/geral/Courses';
import CursoDetail from '../pages/geral/CourseDetail';
import Regulamentos from '../pages/geral/Regulamentos';
import ModalityTypes from '../pages/geral/ModalityTypes.js';
import Torneios from '../pages/geral/Tournaments';
import TorneioDetails from '../pages/geral/TorneioDetails';
import JogoDetails from '../pages/geral/JogoDetails';
import SociosGeral from '../pages/geral/Socios';

// Nucleo admin pages
import Membros from '../pages/nucleo/Membros';
import MemberDetail from '../pages/nucleo/MemberDetail';
import Equipas from '../pages/nucleo/Teams';
import TeamDetailPage from '../pages/nucleo/TeamDetail';
import Jogos from '../pages/nucleo/Jogos';
import MatchDetailPage from '../pages/nucleo/MatchDetail';
import SociosNucleo from '../pages/nucleo/Socios';

// Components
import ProtectedRoute from '../components/ProtectedRoute';
import TestPage from '../pages/TestPage';

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

  if (adminRole === 'general_admin') return <Navigate to="/dashboard" replace />;
  if (adminRole === 'nucleo_admin') return <Navigate to="/dashboard" replace />;
  return <Navigate to="/unauthorized" replace />;
};

export const router = createBrowserRouter([
  // Public/unauthenticated routes
  {
    path: '/',
    element: <RootRedirect />,
  },
  {
    path: '/unauthorized',
    element: <Unauthorized />,
  },

  // Authenticated area with sidebar
  {
    element: <DashboardLayout />, // This layout checks authentication and renders the sidebar
    children: [
      // Global Routes
      { path: '/dashboard',           element: <ProtectedRoute> <Dashboard /></ProtectedRoute> },
      { path: '/test',                element: <ProtectedRoute> <TestPage /></ProtectedRoute> },

      // Geral Admin Routes
      { path: '/geral/administradores',     element: <ProtectedRoute> <Administradores /></ProtectedRoute> },
      { path: '/geral/administradores/:id', element: <ProtectedRoute> <AdminDetailPage /></ProtectedRoute> },
      { path: '/geral/modalidades',         element: <ProtectedRoute> <Modalities /></ProtectedRoute> },
      { path: '/geral/modalidades/:id',     element: <ProtectedRoute> <ModalityDetails /></ProtectedRoute> },
      { path: '/geral/nucleos',             element: <ProtectedRoute> <NucleoListPage /></ProtectedRoute> },
      { path: '/geral/nucleos/:id',         element: <ProtectedRoute> <NucleoDetails /></ProtectedRoute> },
      { path: '/geral/cursos',              element: <ProtectedRoute> <Cursos /></ProtectedRoute> },
      { path: '/geral/cursos/:id',          element: <ProtectedRoute> <CursoDetail /></ProtectedRoute> },
      { path: '/geral/regulamentos',        element: <ProtectedRoute> <Regulamentos /></ProtectedRoute> },
      { path: '/geral/formatos-prova',      element: <ProtectedRoute> <ModalityTypes /></ProtectedRoute> },
      { path: '/geral/torneios',            element: <ProtectedRoute> <Torneios /></ProtectedRoute> },
      { path: '/geral/torneios/:id',        element: <ProtectedRoute> <TorneioDetails /></ProtectedRoute> },
      { path: '/geral/jogos/:id',           element: <ProtectedRoute> <JogoDetails /></ProtectedRoute> },
      { path: '/geral/socios',              element: <ProtectedRoute> <SociosGeral /></ProtectedRoute> },

      // Nucleo Admin Routes
      { path: '/nucleo/socios',             element: <ProtectedRoute> <SociosNucleo /></ProtectedRoute> },
      // { path: '/nucleo/membros',            element: <ProtectedRoute> <Membros /></ProtectedRoute> },
      // { path: '/nucleo/membros/:type/:id',  element: <ProtectedRoute> <MemberDetail /></ProtectedRoute> },
      { path: '/nucleo/equipas',            element: <ProtectedRoute> <Equipas /></ProtectedRoute> },
      { path: '/nucleo/equipas/:id',        element: <ProtectedRoute> <TeamDetailPage /></ProtectedRoute> },
      { path: '/nucleo/jogos',              element: <ProtectedRoute> <Jogos /></ProtectedRoute> },
      { path: '/nucleo/jogos/:id',          element: <ProtectedRoute> <MatchDetailPage /></ProtectedRoute> },
    ],
  },
  // Fallback Route (404)
  {
    path: '*',
    element: <NotFound />,
  },
], {
  basename: '/admin',
});
