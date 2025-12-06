import { apiClient } from './client';

export interface Regulation {
  id: number;
  title: string;
  description?: string;
  modality_id?: number;
  file_url: string;
  created_at: string;
}

export interface RegulationCreate {
  file: File;
  title: string;
  modality_id?: number;
  description?: string;
}

export interface RegulationUpdate {
  title?: string;
  description?: string;
  modality_id?: number;
}

export const regulationsApi = {
  async getAll(): Promise<Regulation[]> {
    return apiClient.get<Regulation[]>('/regulations');
  },

  async getById(id: number): Promise<Regulation> {
    return apiClient.get<Regulation>(`/regulations/${id}`);
  },

  async create(data: RegulationCreate): Promise<Regulation> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('title', data.title);
    if (data.modality_id) {
      formData.append('modality_id', data.modality_id.toString());
    }
    if (data.description) {
      formData.append('description', data.description);
    }

    // Use fetch directly for file upload
    const token = localStorage.getItem('auth_token');
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

    const response = await fetch('/api/admin/regulations', {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Upload failed' }));
      throw new Error(error.error || 'Failed to upload regulation');
    }

    return response.json();
  },

  async update(id: number, data: RegulationUpdate): Promise<Regulation> {
    return apiClient.put<Regulation>(`/regulations/${id}`, data);
  },

  async delete(id: number): Promise<void> {
    return apiClient.delete(`/regulations/${id}`);
  },
};
