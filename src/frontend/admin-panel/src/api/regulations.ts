import { apiClient } from './client';

export interface Regulation {
  id: string;
  title: string;
  file_url: string;
  description?: string;
  created_at: string;
}

export interface RegulationCreate {
  title: string;
  file: File;
  description?: string;
}

export const regulationsApi = {
  async getAll(search?: string): Promise<Regulation[]> {
    const params = search ? { search } : undefined;
    return apiClient.get<Regulation[]>('/regulations/', params);
  },

  async create(data: RegulationCreate): Promise<Regulation> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('title', data.title);
    if (data.description) {
      formData.append('description', data.description);
    }

    return apiClient.post<Regulation>('/regulations/', formData);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/regulations/${id}/`);
  }
};