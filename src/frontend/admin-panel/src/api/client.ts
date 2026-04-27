import keycloak from '../lib/keycloak';

const API_BASE_URL = '/api2/admin';

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
    if (params && typeof params === 'object') {
      const filteredParams = Object.entries(params as Record<string, unknown>)
      .filter(([, value]) => value !== undefined)
      .reduce<Record<string, string>>((acc, [key, value]) => {
        acc[key] = String(value);
        return acc;
      }, {});

      const searchParams = new URLSearchParams(filteredParams);
      const query = searchParams.toString();

      if (query) {
      fullUrl += `?${query}`;
      }
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
    const isFormData = data instanceof FormData;
<<<<<<< HEAD

    // Precisamos do await aqui para obter os headers de autenticação
=======
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd
    const authHeader = await this.getAuthHeader();
    const headers: Record<string, string> = { ...authHeader };

    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: isFormData ? (data as FormData) : JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'API request failed' }));
      throw new Error(error.error || 'Network error');
    }
    return response.json();
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const isFormData = data instanceof FormData;
<<<<<<< HEAD

    // Precisamos do await aqui para obter os headers de autenticação
    const authHeader = await this.getAuthHeader();
    const headers: Record<string, string> = {
      ...authHeader,
    };
=======
    const authHeader = await this.getAuthHeader();
    const headers: Record<string, string> = { ...authHeader };
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd

    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers,
      body: isFormData ? (data as FormData) : JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'API request failed' }));
      throw new Error(error.error || 'Network error');
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

  async getBlob(endpoint: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        ...(await this.getAuthHeader()),
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Network error',
      }));
      throw new Error(error.error || 'API request failed');
    }

    return response.blob();
  }

}

export const apiClient = new ApiClient();
