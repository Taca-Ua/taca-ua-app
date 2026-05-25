import { apiClient } from './client';

export interface NucleoListItem {
  id: string;
  name: string;
  abbreviation: string;
  logo_url: string;
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
  image?: File;
}

export interface NucleoUpdate {
  name?: string;
  abbreviation?: string;
  image?: File;
}

export const nucleosApi = {
  async getAll(): Promise<NucleoListItem[]> {
	return apiClient.get<NucleoListItem[]>('/nucleos/');
  },

  async getById(nucleoId: string): Promise<NucleoDetail> {
	return apiClient.get<NucleoDetail>(`/nucleos/${nucleoId}/`);
  },

  async create(data: NucleoCreate): Promise<NucleoDetail> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('abbreviation', data.abbreviation);
    if (data.image) {
      formData.append('image', data.image);
    }
	return apiClient.post<NucleoDetail>('/nucleos/', formData);
  },

  async update(nucleoId: string, data: NucleoUpdate): Promise<NucleoDetail> {
    const formData = new FormData();
    if (data.name !== undefined) {
      formData.append('name', data.name);
    }
    if (data.abbreviation !== undefined) {
      formData.append('abbreviation', data.abbreviation);
    }
    if (data.image) {
      formData.append('image', data.image);
    }
	return apiClient.put<NucleoDetail>(`/nucleos/${nucleoId}/`, formData);
  },

  async delete(nucleoId: string): Promise<void> {
	return apiClient.delete(`/nucleos/${nucleoId}/`);
  },
};
