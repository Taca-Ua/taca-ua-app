import { apiClient } from './client';

export interface ModalityListItem {
  id: string;
  name: string;
  belongs_to_season: boolean;
  modality_type?: {
    id: string;
    name: string;
  };
};

export interface ModalityDetail extends ModalityListItem {};

export interface ModalityCreate {
  name: string;
  modality_type_id: string;
}

export interface ModalityUpdate {
  name?: string;
  modality_type_id?: string;
  season_id?: number | null;
}

export interface ModalityTypeListParameters {
  season_id?: number;
}

export const modalitiesApi = {
  async getAll(params?: ModalityTypeListParameters): Promise<ModalityListItem[]> {
    return apiClient.get<ModalityListItem[]>('/modalities/', params );
  },

  async create(data: ModalityCreate): Promise<ModalityListItem> {
    return apiClient.post<ModalityListItem>('/modalities/', data);
  },

  async getById(modalityId: string, season_id?: number): Promise<ModalityDetail> {
    return apiClient.get<ModalityDetail>(`/modalities/${modalityId}/`, { season_id });
  },

  async update(modalityId: string, data: ModalityUpdate): Promise<ModalityDetail> {
    return apiClient.put<ModalityDetail>(`/modalities/${modalityId}/`, data);
  },

  async delete(modalityId: string): Promise<void> {
    return apiClient.delete(`/modalities/${modalityId}/`);
  },
};
