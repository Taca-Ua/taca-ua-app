import { createContext } from 'react';
import type { KcRole } from '../lib/jwtRoles';

export interface AuthContextType {
  /** True once Keycloak has finished its init handshake. */
  isLoading: boolean;
  /** True when the user holds a valid Keycloak session. */
  isAuthenticated: boolean;
  /** Raw access token kept in memory only – never persisted to storage. */
  token: string | null;
  /** All realm roles extracted from the token payload. */
  roles: string[];
  /** The recognised admin role ('general_admin' | 'nucleo_admin') or null. */
  adminRole: KcRole | null;
  /** preferred_username from the token. */
  username: string | null;
  /** Redirect to Keycloak login page. */
  login: () => void;
  /** End the Keycloak session and redirect back to the app root. */
  logout: () => void;
  /** Convenience: check whether a specific KcRole is held. */
  hasRole: (role: KcRole) => boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
