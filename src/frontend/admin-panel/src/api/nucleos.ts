import { apiClient } from './client';

export interface Nucleo {
  id: string;
  name: string;
  abbreviation: string;
}

export interface NucleoCreate {
  name: string;
  abbreviation: string;
}

export const nucleosApi = {
  async getAll(): Promise<Nucleo[]> {
	return apiClient.get<Nucleo[]>('/nucleos');
  },

  async getById(nucleoId: string): Promise<Nucleo> {
	return apiClient.get<Nucleo>(`/nucleos/${nucleoId}`);
  },

  async create(data: NucleoCreate): Promise<Nucleo> {
	return apiClient.post<Nucleo>('/nucleos', data);
  },

  async update(nucleoId: string, data: Partial<NucleoCreate>): Promise<Nucleo> {
	return apiClient.put<Nucleo>(`/nucleos/${nucleoId}`, data);
  },

  async delete(nucleoId: string): Promise<void> {
	return apiClient.delete(`/nucleos/${nucleoId}`);
  },
};
