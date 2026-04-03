import { apiClient } from './client';

export interface Nucleo {
  id: string;
  name: string;
  abbreviation: string;
  logo_url?: string;
}

export interface NucleoDetail extends Nucleo {
  // Additional fields can be added here if needed
}

export interface NucleoCreate {
  name: string;
  abbreviation: string;
}

export interface NucleoUpdate {
  name?: string;
  abbreviation?: string;
}

export const nucleosApi = {
  async getAll(): Promise<Nucleo[]> {
	return apiClient.get<Nucleo[]>('/nucleos/');
  },

  async getById(nucleoId: string): Promise<Nucleo> {
	return apiClient.get<Nucleo>(`/nucleos/${nucleoId}/`);
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
