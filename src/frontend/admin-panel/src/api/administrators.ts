import { apiClient } from './client';

export interface Administrator {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: 'geral' | 'nucleo';
  course_id: number | null;
  course_abbreviation: string | null;
  password?: string; // Only returned in detail view
}

export interface AdministratorCreate {
  username: string;
  password: string;
  full_name: string;
  email: string;
  role: 'geral' | 'nucleo';
  course_id?: number;
}

export interface AdministratorUpdate {
  username?: string;
  full_name?: string;
  email?: string;
  password?: string;
  course_id?: number;
}

export const administratorsApi = {
  async getAll(): Promise<Administrator[]> {
    return apiClient.get<Administrator[]>('/administrators');
  },

  async getById(administratorId: number): Promise<Administrator> {
    return apiClient.get<Administrator>(`/administrators/${administratorId}`);
  },

  async create(data: AdministratorCreate): Promise<Administrator> {
    return apiClient.post<Administrator>('/administrators', data);
  },

  async update(administratorId: number, data: AdministratorUpdate): Promise<Administrator> {
    return apiClient.put<Administrator>(`/administrators/${administratorId}`, data);
  },

  async delete(administratorId: number): Promise<void> {
    return apiClient.delete(`/administrators/${administratorId}`);
  },
};
