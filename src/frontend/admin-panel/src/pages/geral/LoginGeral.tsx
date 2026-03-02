import { useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';

/**
 * LoginGeral is no longer used as a route - Keycloak handles the login
 * redirect via AuthProvider (onLoad: 'login-required').
 * This component is kept for backwards compatibility and will trigger
 * the Keycloak login flow if somehow rendered.
 */
function LoginGeral() {
  const { login } = useAuth();

  useEffect(() => {
    login();
  }, [login]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600" />
    </div>
  );
}

export default LoginGeral;
