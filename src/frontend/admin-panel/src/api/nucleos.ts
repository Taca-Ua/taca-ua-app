import { apiClient } from './client';

export interface NucleoListItem {
  id: string;
  name: string;
  abbreviation: string;
  logo_url?: string;
  belongs_to_season?: boolean;
}

export interface NucleoDetail extends NucleoListItem {
  courses: {
    id: string;
    name: string;
    abbreviation: string;
  }[];

  relevant_season_ids: number[];
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
  async getAll(seasonId?: number): Promise<NucleoListItem[]> {
	return apiClient.get<NucleoListItem[]>('/nucleos/', { season_id: seasonId });
  },

  async getById(nucleoId: string, seasonId?: number): Promise<NucleoDetail> {
	return apiClient.get<NucleoDetail>(`/nucleos/${nucleoId}/`, { season_id: seasonId });
  },

  async create(data: NucleoCreate, seasonId?: number): Promise<NucleoDetail> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('abbreviation', data.abbreviation);
    if (data.image) {
      formData.append('image', data.image);
    }
	return apiClient.post<NucleoDetail>('/nucleos/', formData, { season_id: seasonId });
  },

  async update(nucleoId: string, data: NucleoUpdate, seasonId?: number): Promise<NucleoDetail> {
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
	return apiClient.put<NucleoDetail>(`/nucleos/${nucleoId}/`, formData, { season_id: seasonId });
  },

  async addToSeason(nucleoId: string, seasonId: number): Promise<NucleoDetail> {
    return apiClient.put<NucleoDetail>(`/nucleos/${nucleoId}/add_to_season/${seasonId}/`, {}, { season_id: seasonId });
  },

  async removeFromSeason(nucleoId: string, seasonId: number): Promise<NucleoDetail> {
    return apiClient.put<NucleoDetail>(`/nucleos/${nucleoId}/remove_from_season/${seasonId}/`, {}, { season_id: seasonId });
  }
};
