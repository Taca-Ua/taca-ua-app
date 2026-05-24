import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: `${window.location.origin}/auth`,
  realm: "taca-ua",
  clientId: 'frontend-admin',
});

export default keycloak;
