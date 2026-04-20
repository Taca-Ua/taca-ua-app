import { useState, useEffect, useRef, useCallback } from 'react';
import type { ReactNode } from 'react';
import keycloak from '../lib/keycloak';
import { AuthContext } from './AuthContext';
import type { AuthContextType } from './AuthContext';
import { extractRealmRoles, getAdminRole } from '../lib/jwtRoles';
import type { KcRole } from '../lib/jwtRoles';

/**
 * How often (ms) we proactively check whether the token needs refreshing.
 * Keycloak's onTokenExpired callback is a fallback; the interval catches
 * tokens that are about to expire before the callback fires.
 */
const REFRESH_CHECK_INTERVAL_MS = 60_000;

/**
 * Refresh the token if it expires within this many seconds.
 * Keeps at least 30 s of validity headroom at all times.
 */
const TOKEN_MIN_VALIDITY_SEC = 30;

// ---------------------------------------------------------------------------

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  // Token lives in React state only – never written to localStorage / sessionStorage.
  const [token, setToken] = useState<string | null>(null);
  const [roles, setRoles] = useState<string[]>([]);
  const [adminRole, setAdminRole] = useState<KcRole | null>(null);
  const [username, setUsername] = useState<string | null>(null);

  const refreshTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // Guard against double-invocation in React 18 StrictMode.
  const initializedRef = useRef(false);

  // -------------------------------------------------------------------------
  // Sync component state from the keycloak instance (call after any token change)
  // -------------------------------------------------------------------------
  const syncFromKeycloak = useCallback(() => {
    const t = keycloak.token ?? null;
    setToken(t);
    setIsAuthenticated(keycloak.authenticated ?? false);
    setUsername(keycloak.tokenParsed?.['preferred_username'] as string ?? null);

    if (t) {
      const r = extractRealmRoles(t);
      setRoles(r);
      setAdminRole(getAdminRole(r));
    } else {
      setRoles([]);
      setAdminRole(null);
    }
  }, []);

  // -------------------------------------------------------------------------
  // Proactive token refresh loop
  // -------------------------------------------------------------------------
  const startRefreshLoop = useCallback(() => {
    if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);

    refreshTimerRef.current = setInterval(async () => {
      try {
        const refreshed = await keycloak.updateToken(TOKEN_MIN_VALIDITY_SEC);
        if (refreshed) syncFromKeycloak();
      } catch {
        // Refresh token has expired – force re-login.
        keycloak.login();
      }
    }, REFRESH_CHECK_INTERVAL_MS);
  }, [syncFromKeycloak]);

  // -------------------------------------------------------------------------
  // Keycloak initialisation (runs once)
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    keycloak
      .init({
        /**
         * 'login-required' – redirect unauthenticated users to Keycloak
         * immediately.  No custom login form needed.
         */
        onLoad: 'login-required',
        /**
         * Disable the hidden iframe that polls Keycloak for session state
         * (causes CORS issues in many setups).
         */
        checkLoginIframe: false,
        /** PKCE with S256 is required for public clients. */
        pkceMethod: 'S256',
      })
      .then((authenticated) => {
        if (authenticated) {
          syncFromKeycloak();
          startRefreshLoop();
        }
        setIsLoading(false);
      })
      .catch(() => {
        // Init failed (network error, wrong config, etc.)
        setIsLoading(false);
      });

    // Keycloak fires this when the token expires naturally.
    keycloak.onTokenExpired = () => {
      keycloak
        .updateToken(TOKEN_MIN_VALIDITY_SEC)
        .then(syncFromKeycloak)
        .catch(() => keycloak.login());
    };

    return () => {
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
    };
  }, [syncFromKeycloak, startRefreshLoop]);

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------
  const login = useCallback(() => keycloak.login(), []);

  const logout = useCallback(
    () =>
      keycloak.logout({
        redirectUri: window.location.origin + '/admin',
      }),
    [],
  );

  const hasRole = useCallback(
    (role: KcRole) => roles.includes(role),
    [roles],
  );

  const value: AuthContextType = {
    isLoading,
    isAuthenticated,
    token,
    roles,
    adminRole,
    username,
    login,
    logout,
    hasRole,
    isAdminGeneral: adminRole === 'general_admin',
    isAdminNucleo: adminRole === 'nucleo_admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
