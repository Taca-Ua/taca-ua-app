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
import Equipas from '../pages/nucleo/Teams';
import TeamDetailPage from '../pages/nucleo/TeamDetail';
import Jogos from '../pages/nucleo/Jogos';

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
      { path: '/administradores',     element: <ProtectedRoute> <Administradores /></ProtectedRoute> },
      { path: '/administradores/:id', element: <ProtectedRoute> <AdminDetailPage /></ProtectedRoute> },
      { path: '/modalidades',         element: <ProtectedRoute> <Modalities /></ProtectedRoute> },
      { path: '/modalidades/:id',     element: <ProtectedRoute> <ModalityDetails /></ProtectedRoute> },
      { path: '/nucleos',             element: <ProtectedRoute> <NucleoListPage /></ProtectedRoute> },
      { path: '/nucleos/:id',         element: <ProtectedRoute> <NucleoDetails /></ProtectedRoute> },
      { path: '/cursos',              element: <ProtectedRoute> <Cursos /></ProtectedRoute> },
      { path: '/cursos/:id',          element: <ProtectedRoute> <CursoDetail /></ProtectedRoute> },
      { path: '/regulamentos',        element: <ProtectedRoute> <Regulamentos /></ProtectedRoute> },
      { path: '/formatos-prova',      element: <ProtectedRoute> <ModalityTypes /></ProtectedRoute> },
      { path: '/torneios',            element: <ProtectedRoute> <Torneios /></ProtectedRoute> },
      { path: '/torneios/:id',        element: <ProtectedRoute> <TorneioDetails /></ProtectedRoute> },
      { path: '/jogos/:id',           element: <ProtectedRoute> <JogoDetails /></ProtectedRoute> },
      { path: '/membros',             element: <ProtectedRoute> <SociosGeral /></ProtectedRoute> },

      // Nucleo Admin Routes
      { path: '/equipas',            element: <ProtectedRoute> <Equipas /></ProtectedRoute> },
      { path: '/equipas/:id',        element: <ProtectedRoute> <TeamDetailPage /></ProtectedRoute> },
      { path: '/jogos',              element: <ProtectedRoute> <Jogos /></ProtectedRoute> },
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
