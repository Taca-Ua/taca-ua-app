import { apiClient } from './client';

export interface Admin {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  roles: string[];
  enabled: boolean;
}

export interface AdminDetails extends Admin {
}

export interface AdminCreate {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  roles: string[];
}

export interface AdminUpdate {
  email?: string;
  first_name?: string;
  last_name?: string;
  enabled?: boolean;
}

export interface AdminPasswordChange {
  new_password: string;
  temporary: boolean;
}


export const administratorsApi = {
  async getAll(): Promise<Admin[]> {
    return apiClient.get<Admin[]>('/admins/');
  },

  async create(data: AdminCreate): Promise<Admin> {
    return apiClient.post<Admin>('/admins/', data);
  },

  async getById(administratorId: number): Promise<AdminDetails> {
    return apiClient.get<AdminDetails>(`/admins/${administratorId}/`);
  },

  async update(administratorId: number, data: AdminUpdate): Promise<Admin> {
    return apiClient.put<Admin>(`/admins/${administratorId}/`, data);
  },

  async changePassword(administratorId: number, data: AdminPasswordChange): Promise<void> {
    return apiClient.post(`/admins/${administratorId}/change-password/`, data);
  },

  async delete(administratorId: number): Promise<void> {
    return apiClient.delete(`/admins/${administratorId}/`);
  },
};
