import { Navigate } from 'react-router-dom';
import { useKeycloak } from '../auth/KeycloakProvider';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { authenticated, loading, hasRole } = useKeycloak();

  if (loading) {
    return <div>Loading...</div>;
  }

  // Si no está autenticado, redirige a la página de inicio de sesión
  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si requiere un rol y el usuario no lo tiene, redirige a acceso denegado
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Si pasa todas las validaciones
  return <>{children}</>;
};

export default ProtectedRoute;
