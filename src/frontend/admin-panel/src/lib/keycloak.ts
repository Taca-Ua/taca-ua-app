import Keycloak from 'keycloak-js';

/**
 * Singleton Keycloak instance.
 * Configuration is sourced from Vite env variables with safe fallbacks.
 *
 * Required .env (or docker env) variables:
 *   VITE_KEYCLOAK_URL        – e.g. http://localhost:8080
 *   VITE_KEYCLOAK_REALM      – e.g. taca-ua
 *   VITE_KEYCLOAK_CLIENT_ID  – e.g. admin-panel
 */
const keycloak = new Keycloak({
  // Keycloak is proxied by nginx at /keycloak/ – the fallback mirrors that.
  url: import.meta.env.VITE_KEYCLOAK_URL ?? 'http://localhost/keycloak',
  realm: import.meta.env.VITE_KEYCLOAK_REALM ?? 'taca-ua',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID ?? 'frontend-admin',
});

export default keycloak;
