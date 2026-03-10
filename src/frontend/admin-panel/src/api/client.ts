import keycloak from '../lib/keycloak';

const API_BASE_URL = '/api/admin';

interface ApiError {
  error: string;
  details?: unknown;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Remove any stale legacy session token that the old mock auth may have
    // written to localStorage.  The real Keycloak token lives in memory only.
    localStorage.removeItem('auth_token');
  }

  /**
   * Proactively refresh the Keycloak access token if it expires within 30 s,
   * then return the Authorization header map ready for fetch().
   */
  private async getAuthHeader(): Promise<Record<string, string>> {
    if (!keycloak.authenticated) return {};
    try {
      await keycloak.updateToken(30);
    } catch {
      // Refresh token has expired – redirect the user to Keycloak login.
      keycloak.login();
      return {};
    }
    return keycloak.token ? { Authorization: `Bearer ${keycloak.token}` } : {};
  }

  async get<T>(endpoint: string, params?: unknown): Promise<T> {
    let fullUrl = `${this.baseUrl}${endpoint}`;

    // If params exist, append them as query string
    if (params) {
      const searchParams = new URLSearchParams(params as Record<string, string>);
      fullUrl += `?${searchParams.toString()}`;
    }

    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(await this.getAuthHeader()),
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Network error',
      }));
      throw new Error(error.error || 'API request failed');
    }

    return response.json();
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(await this.getAuthHeader()),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Network error',
      }));
      const new_error = new Error(error.error || 'API request failed');
      throw new_error;
    }

    return response.json();
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(await this.getAuthHeader()),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Network error',
      }));
      throw new Error(error.error || 'API request failed');
    }

    return response.json();
  }

  async delete(endpoint: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(await this.getAuthHeader()),
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Network error',
      }));
      throw new Error(error.error || 'API request failed');
    }
  }
}

export const apiClient = new ApiClient();
