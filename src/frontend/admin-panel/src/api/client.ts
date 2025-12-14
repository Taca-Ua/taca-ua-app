const API_BASE_URL = '/api/admin';

interface ApiError {
  error: string;
  details?: unknown;
}

// ============================================
// KEYCLOAK INTEGRATION SETUP
// ============================================

// Global variables to hold the token retrieval and 401 handling functions.
// These are injected from the KeycloakProvider.
let globalGetToken: (() => string | undefined) | undefined = undefined;
let globalUnauthorizedHandler: (() => void) | undefined = undefined;

/**
 * Sets up the API client dependencies with the Keycloak authentication logic.
 * This must be called once Keycloak is initialized.
 * @param getTokenFn - Function to retrieve the current Access Token from Keycloak state (in memory).
 * @param unauthorizedHandlerFn - Function to execute upon receiving HTTP 401 (e.g., keycloak.login()).
 */
export const setupApiClient = (
  getTokenFn: () => string | undefined,
  unauthorizedHandlerFn: () => void
) => {
  globalGetToken = getTokenFn;
  globalUnauthorizedHandler = unauthorizedHandlerFn;
  console.log('API Client successfully integrated with Keycloak token provider.');
};


export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // CRITICAL CHANGE: Get token from the injected function (Keycloak state)
  // NOT from localStorage (Security fix).
  private getAuthHeader(): Record<string, string> {
    const token = globalGetToken ? globalGetToken() : undefined;

    // SECURITY FIX: localStorage usage REMOVED.

    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  }

  // Helper function to handle response and 401 errors
  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.ok) {
      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }
      return response.json();
    }

    // CRITICAL CHANGE: Handle 401 Unauthorized
    if (response.status === 401) {
      console.warn('API request returned 401 (Unauthorized). Forcing Keycloak re-login.');

      if (globalUnauthorizedHandler) {
        // Calls the function injected by KeycloakProvider (keycloak.login())
        globalUnauthorizedHandler();
      }

      // Throw error and return a pending promise to stop execution in the caller
      // Esto previene que el código posterior al llamado a la API se ejecute
      return new Promise<T>(() => {
        throw new Error('Unauthorized or Token Expired. Redirecting to login.');
      });
    }

    // Handle other errors (4xx, 5xx)
    const error: ApiError = await response.json().catch(() => ({
      error: `Server error (${response.status})`,
    }));

    throw new Error(error.error || `API request failed with status ${response.status}`);
  }

  // --- GET METHOD ---
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    let fullUrl = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      fullUrl += `?${searchParams.toString()}`;
    }

    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
    });

    return this.handleResponse(response);
  }

  // --- POST METHOD ---
  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  }

  // --- PUT METHOD ---
  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  }

  // --- DELETE METHOD ---
  async delete(endpoint: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
    });

    return this.handleResponse(response) as Promise<void>;
  }
}

export const apiClient = new ApiClient();
