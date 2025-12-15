import Keycloak from 'keycloak-js';
import { createContext, useContext, useEffect, useState, useRef } from 'react';
import { setupApiClient } from '../api/client';

// Keycloak Configuration Object
const keycloak = new Keycloak({
  url: 'http://localhost/keycloak',
  realm: 'taca-ua',
  clientId: 'api-client',
});

// Define the Context structure
interface KeycloakContextType {
  keycloak: Keycloak;
  authenticated: boolean;
  loading: boolean;
  token?: string;
  login: () => void;
  logout: () => void;
  hasRole: (role: string) => boolean;
}

const KeycloakContext = createContext<KeycloakContextType | null>(null);

export const KeycloakProvider = ({ children }: { children: React.ReactNode }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | undefined>(undefined);

  // Usamos useRef para garantizar que el init() solo se intente una vez
  const initAttempted = useRef(false);

  useEffect(() => {
    let refreshInterval: number;

    // Evitar doble inicialización en modo React Strict
    if (initAttempted.current) {
        return;
    }
    initAttempted.current = true;

    // Initialization of Keycloak adapter
    keycloak
      .init({
        onLoad: 'check-sso',
        pkceMethod: 'S256',
        silentCheckSsoRedirectUri:
          window.location.origin + '/silent-check-sso.html',
        checkLoginIframe: false,
      })
      .then((auth) => {
        setAuthenticated(auth);
        setLoading(false);
        setToken(keycloak.token);

        if (auth) {

          const getToken = () => keycloak.token;


          const handle401 = () => {
            console.warn("401 detected by API client. Attempting token refresh.");

            keycloak.updateToken(30)
                .then(() => {

                    console.log("Token successfully refreshed after 401.");
                })
                .catch(() => {
                    console.error("Token refresh failed after 401. Forcing login.");
                    // Si el refresh falla, entonces sí, forzar el login (redirección)
                    keycloak.login();
                });
          };


          setupApiClient(getToken, handle401);

          // Token automatic refresh interval (checks every minute)
          refreshInterval = window.setInterval(() => {
            keycloak
              .updateToken(60)
              .then((refreshed) => {
                if (refreshed) {
                  setToken(keycloak.token);
                  console.log('Token successfully refreshed.');
                }
              })
              .catch(() => {
                console.error('Token refresh failed (Periodic Check)');
                keycloak.login();
              });
          }, 60000); // Check every minute
        }
      })
      .catch((error) => {
        console.error('Keycloak init failed', error);
        setLoading(false);
      });

    // Cleanup function for the interval
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  // Wrapper function for Keycloak login
  const login = () => keycloak.login();

  // Wrapper function for Keycloak logout (clear local state and redirect)
  const logout = () => {
    // Nota: Aunque no se ve explícitamente en este código, se recomienda limpiar
    // sessionStorage/localStorage si se usan para otros datos.
    keycloak.logout({
      redirectUri: window.location.origin,
    });
  }

  // Wrapper function for role checking
  const hasRole = (role: string) =>
    keycloak.hasRealmRole(role);

  return (
    <KeycloakContext.Provider
      value={{
        keycloak,
        authenticated,
        loading,
        token,
        login,
        logout,
        hasRole,
      }}
    >
      {children}
    </KeycloakContext.Provider>
  );
};

export const useKeycloak = () => {
  const context = useContext(KeycloakContext);
  if (!context) {
    throw new Error('useKeycloak must be used within KeycloakProvider');
  }
  return context;
};
