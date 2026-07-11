import keycloak from '../lib/keycloak';

const API_BASE_URL = '/api/admin';

export class ApiError extends Error {
  public status: number;
  public body?: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
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

  private async throwApiError(response: Response): Promise<never> {
    const body = await response.json().catch(() => ({}));

    if (!body) {
      throw new ApiError('API request failed', response.status);
    }
    if (body instanceof Array) {
      throw new ApiError(body[0] || 'API request failed', response.status, body);
    } else if (typeof body === 'object') {
      let message = '';
      // iterate over the keys of the body object and concatenate the messages
      for (const key in body) {
        if (body.hasOwnProperty(key)) {
          const value = body[key];
          if (Array.isArray(value)) {
            message += `${key}: ${value.join(', ')}\n`;
          } else {
            message += `${key}: ${value}\n`;
          }
        }
      }
      throw new ApiError(message || 'API request failed', response.status, body);
    } else {
      throw new ApiError('API request failed', response.status, body);
    }
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
      const body = await response.json().catch(() => ({}));
      throw new ApiError(body.detail || body.error || 'API request failed', response.status, body);
    }

    return response.json();
  }

  async post<T>(endpoint: string, data: unknown, params?: unknown): Promise<T> {

    // Similar to get(), we need to append params as query string if they exist
    let fullUrl = `${this.baseUrl}${endpoint}`;
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

    const isFormData = data instanceof FormData;

    // Precisamos do await aqui para obter os headers de autenticação
    const authHeader = await this.getAuthHeader();

    const headers: Record<string, string> = {
      ...authHeader,
    };

    // Se for FormData (ficheiro), o fetch define o Content-Type automaticamente com o boundary correto
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(fullUrl, {
      method: 'POST',
      headers,
      body: isFormData ? (data as FormData) : JSON.stringify(data),
    });

    if (!response.ok) {
      await this.throwApiError(response);
    }

    return response.json();
  }

  async put<T>(endpoint: string, data: unknown, params?: unknown): Promise<T> {

    // Similar to get(), we need to append params as query string if they exist
    let fullUrl = `${this.baseUrl}${endpoint}`;
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

    const isFormData = data instanceof FormData;

    // Precisamos do await aqui para obter os headers de autenticação
    const authHeader = await this.getAuthHeader();
    const headers: Record<string, string> = {
      ...authHeader,
    };

    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(fullUrl, {
      method: 'PUT',
      headers,
      body: isFormData ? (data as FormData) : JSON.stringify(data),
    });

    if (!response.ok) {
      await this.throwApiError(response);
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
      await this.throwApiError(response);
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
      const body = await response.json().catch(() => ({}));
      throw new ApiError(body.detail || body.error || 'API request failed', response.status, body);
    }

    return response.blob();
  }

}

export const apiClient = new ApiClient();
