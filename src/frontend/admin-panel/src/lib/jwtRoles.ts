/**
 * Keycloak role extraction utilities.
 *
 * Keycloak stores realm-level roles in the JWT under:
 *   payload.realm_access.roles  → string[]
 *
 * NOTE: We trust the token's authenticity because it was issued by Keycloak
 * and verified server-side on every API call. Parsing the payload here is
 * purely for UI routing decisions – the backend must re-validate the token.
 */

export type KcRole = 'general_admin' | 'nucleo_admin';

/** Decode a JWT payload without verifying the signature. */
function decodePayload(token: string): Record<string, unknown> | null {
  try {
    const [, payload] = token.split('.');
    // base64url → base64 → binary → JSON
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(json) as Record<string, unknown>;
  } catch {
    return null;
  }
}

/** Return all realm-level roles present in the token. */
export function extractRealmRoles(token: string): string[] {
  const payload = decodePayload(token);
  if (!payload) return [];
  const realmAccess = payload.realm_access as { roles?: string[] } | undefined;
  return realmAccess?.roles ?? [];
}

/**
 * Return the highest-priority recognised admin role from the role list,
 * or null if the user holds neither.
 */
export function getAdminRole(roles: string[]): KcRole | null {
  if (roles.includes('general_admin')) return 'general_admin';
  if (roles.includes('nucleo_admin')) return 'nucleo_admin';
  return null;
}
