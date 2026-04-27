import { apiClient } from './client';

export interface NucleoListItem {
  id: string;
  name: string;
  abbreviation: string;
}

export interface NucleoDetail extends NucleoListItem {
  courses: {
    id: string;
    name: string;
    abbreviation: string;
  }[];
};

export interface NucleoCreate {
  name: string;
  abbreviation: string;
}

export interface NucleoUpdate {
  name?: string;
  abbreviation?: string;
}

export const nucleosApi = {
  async getAll(): Promise<NucleoListItem[]> {
	return apiClient.get<NucleoListItem[]>('/nucleos/');
  },

  async getById(nucleoId: string): Promise<NucleoDetail> {
	return apiClient.get<NucleoDetail>(`/nucleos/${nucleoId}/`);
  },

  async create(data: NucleoCreate): Promise<NucleoDetail> {
	return apiClient.post<NucleoDetail>('/nucleos/', data);
  },

  async update(nucleoId: string, data: NucleoUpdate): Promise<NucleoDetail> {
	return apiClient.put<NucleoDetail>(`/nucleos/${nucleoId}/`, data);
  },

  async delete(nucleoId: string): Promise<void> {
	return apiClient.delete(`/nucleos/${nucleoId}/`);
  },
};
