import { apiClient } from './client';
import { type Nucleo } from "./nucleos";

export interface Admin {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  enabled: boolean;
}

export interface AdminDetails extends Admin {
    nucleos: Nucleo[];
}

export interface AdminCreate {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: string;
  nucleos: string[]; // Array of Nucleo IDs
}

export interface AdminUpdate {
  email?: string;
  first_name?: string;
  last_name?: string;
  enabled?: boolean;
  nucleos?: string[]; // Array of Nucleo IDs
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

  async getById(administratorId: string): Promise<AdminDetails> {
    return apiClient.get<AdminDetails>(`/admins/${administratorId}/`);
  },

  async update(administratorId: string, data: AdminUpdate): Promise<Admin> {
    return apiClient.put<Admin>(`/admins/${administratorId}/`, data);
  },

  async changePassword(administratorId: string, data: AdminPasswordChange): Promise<void> {
    return apiClient.post(`/admins/${administratorId}/password/`, data);
  },

  async delete(administratorId: string): Promise<void> {
    return apiClient.delete(`/admins/${administratorId}/`);
  },
};
