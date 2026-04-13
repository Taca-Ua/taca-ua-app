import { apiClient } from './client2';

export interface AdminListItem {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  enabled: boolean;
}

export interface AdminDetail extends AdminListItem {
    nucleos: {
        id: string;
        name: string;
        abbreviation: string;
    }[];
    courses: {
      id: string;
      name: string;
      abbreviation: string;
    }[];
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
  async getAll(): Promise<AdminListItem[]> {
    return apiClient.get<AdminListItem[]>('/admins/');
  },

  async create(data: AdminCreate): Promise<AdminListItem> {
    return apiClient.post<AdminListItem>('/admins/', data);
  },

  async getById(administratorId: string): Promise<AdminDetail> {
    return apiClient.get<AdminDetail>(`/admins/${administratorId}/`);
  },

  async update(administratorId: string, data: AdminUpdate): Promise<AdminDetail> {
    return apiClient.put<AdminDetail>(`/admins/${administratorId}/`, data);
  },

  async delete(administratorId: string): Promise<void> {
    return apiClient.delete(`/admins/${administratorId}/`);
  },

  async changePassword(administratorId: string, data: AdminPasswordChange): Promise<void> {
    return apiClient.post(`/admins/${administratorId}/password/`, data);
  },
};
