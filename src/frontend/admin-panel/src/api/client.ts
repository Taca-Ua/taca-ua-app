const API_BASE_URL = '/api/admin';

interface ApiError {
  error: string;
  details?: unknown;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('auth_token');
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  }

  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    let fullUrl = `${this.baseUrl}${endpoint}`;

    // If params exist, append them as query string
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
        ...this.getAuthHeader(),
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

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
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
        ...this.getAuthHeader(),
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
