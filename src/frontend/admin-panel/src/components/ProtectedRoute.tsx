import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { KcRole } from '../lib/jwtRoles';

/**
 * Route-level role names (used in the router definition).
 * These are mapped to the actual Keycloak realm roles below.
 */
type RouteRole = 'geral' | 'nucleo';

/**
 * Maps the router-level role shorthand to the Keycloak realm role string.
 *   geral  → general_admin
 *   nucleo → nucleo_admin
 */
const KC_ROLE_MAP: Record<RouteRole, KcRole> = {
  geral: 'general_admin',
  nucleo: 'nucleo_admin',
};

interface ProtectedRouteProps {
  children: React.ReactNode;
  /** If provided, the user must hold the matching Keycloak realm role. */
  requiredRole?: RouteRole;
}

// ---------------------------------------------------------------------------

const ProtectedRoute = ({ children, requiredRole }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, adminRole } = useAuth();

  // ------------------------------------------------------------------
  // 1. Still initialising – show spinner while Keycloak resolves.
  // ------------------------------------------------------------------
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto" />
          <p className="mt-4 text-gray-600">A carregar…</p>
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------
  // 2. Not authenticated.
  //    With onLoad:'login-required' Keycloak will have already redirected
  //    the user.  This branch is a safety net (e.g. token invalidated
  //    mid-session).
  // ------------------------------------------------------------------
  if (!isAuthenticated) {
    // keycloak.login() is called inside AuthProvider on token expiry; if we
    // somehow reach this render we just show nothing while the redirect fires.
    return null;
  }

  // ------------------------------------------------------------------
  // 3. Authenticated but holds no recognised admin role.
  // ------------------------------------------------------------------
  if (!adminRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  // ------------------------------------------------------------------
  // 4. Route requires a specific role – verify the user holds it.
  // ------------------------------------------------------------------
  if (requiredRole && adminRole !== KC_ROLE_MAP[requiredRole]) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
