import { useAuth } from '../hooks/useAuth';
import Sidebar from '../components/Sidebar';
import { Navigate, Outlet } from 'react-router-dom';
import { ModalProvider } from '../contexts/ModalContext';

/**
 * DashboardLayout wraps all authenticated pages with a sidebar and main content area.
 * Only renders if the user is authenticated.
 */
export default function DashboardLayout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/unauthorized" replace />;
  }

  return (
    <div className="flex min-h-screen">
      <ModalProvider>
        <Sidebar />
        <main className="flex-1 p-6 bg-gray-50">
          <Outlet />
        </main>
      </ModalProvider>
    </div>
  );
}
