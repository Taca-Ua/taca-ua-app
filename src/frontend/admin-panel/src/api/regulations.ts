import { apiClient } from './client';

export interface RegulationListItem {
  id: string;
  title: string;
  file_url: string;
  description?: string;
  created_at: string;
}

export interface RegulationDetail extends RegulationListItem {
  // Additional fields can be added here if needed in the future
}

export interface RegulationCreate {
  title: string;
  file: File;
  description?: string;
  season_id?: number;
}

export interface RegulationUpdate {
  title?: string;
  file?: File;
  description?: string;
}

export const regulationsApi = {
  async getAll(params?: { season_id?: number }): Promise<RegulationListItem[]> {
    return apiClient.get<RegulationListItem[]>('/regulations/', params);
  },

  async create(data: RegulationCreate): Promise<RegulationListItem> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('title', data.title);
    formData.append('season_id', data.season_id?.toString() ?? '');
    if (data.description) {
      formData.append('description', data.description);
    }

    return apiClient.post<RegulationListItem>('/regulations/', formData);
  },

  async getById(id: string): Promise<RegulationDetail> {
    return apiClient.get<RegulationDetail>(`/regulations/${id}/`);
  },

  async update(id: string, data: Partial<RegulationUpdate>): Promise<RegulationDetail> {
    const formData = new FormData();
    if (data.file) {
      formData.append('file', data.file);
    }
    if (data.title) {
      formData.append('title', data.title);
    }
    if (data.description) {
      formData.append('description', data.description);
    }
    console.log('Updating regulation with ID:', id);
    console.log('FormData entries:');
    formData.forEach((value, key) => {
      if (value instanceof File) {
        console.log(`  ${key}: [File] ${value.name}`);
      } else {
        console.log(`  ${key}: ${value}`);
      }
    });

    return apiClient.put<RegulationDetail>(`/regulations/${id}/`, formData);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/regulations/${id}/`);
  }
};
