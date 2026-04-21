import { apiClient } from './client';

export interface StaffListItem {
  id: string;
  full_name: string;
  staff_number?: string;
  contact?: string;
}

export interface StaffDetail extends StaffListItem {
  // Additional fields can be added here if needed
}

export interface StaffCreate {
  full_name: string;
  staff_number: string;
  contact: string;
}

export interface StaffUpdate {
  full_name?: string;
  staff_number?: string;
  contact?: string;
}

export const staffApi = {
  async getAll(): Promise<StaffListItem[]> {
    return apiClient.get<StaffListItem[]>('/staff/');
  },

  async create(data: StaffCreate): Promise<StaffListItem> {
    return apiClient.post<StaffListItem>('/staff/', data);
  },

  async getById(id: string): Promise<StaffDetail> {
    return apiClient.get<StaffDetail>(`/staff/${id}/`);
  },

  async update(id: string, data: StaffUpdate): Promise<StaffDetail> {
    return apiClient.put<StaffDetail>(`/staff/${id}/`, data);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/staff/${id}/`);
  },
};
