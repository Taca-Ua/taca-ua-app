import { apiClient } from './client';

export interface ModalityListItem {
  id: string;
  name: string;
  belongs_to_season?: boolean;
  modality_type?: {
    id: string;
    name: string;
  };
};

export interface ModalityDetail extends ModalityListItem {
  relevant_seasons_ids: number[];  // List of season IDs where this modality is relevant (active)
  regulation?: {
    id: string;
    name: string;
    link: string;
  };  // Optional regulation information, can be null if no regulation is associated
  point_unit: string;
};

export interface ModalityCreate {
  name: string;
  modality_type_id: string;
}

export interface ModalityUpdate {
  name?: string;
  modality_type_id?: string;
  season_id?: number;
  point_unit?: string;
}

export interface ModalityTypeListParameters {
  season_id?: number;
}

export interface ModalityUpdateRegulation {
  regulation_id?: string | null;
  season_id: number;
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

  async update(modalityId: string, data: ModalityUpdate, season_id?: number): Promise<ModalityDetail> {
    return apiClient.put<ModalityDetail>(`/modalities/${modalityId}/`, data, { season_id });
  },

  async addToSeason(modalityId: string, seasonId: number, modalityTypeId: string): Promise<ModalityDetail> {
    return apiClient.post<ModalityDetail>(`/modalities/${modalityId}/season/${seasonId}/`, { modality_type_id: modalityTypeId });
  },

  async removeFromSeason(modalityId: string, seasonId: number): Promise<ModalityDetail> {
    return apiClient.put<ModalityDetail>(`/modalities/${modalityId}/season/${seasonId}/`, { });
  },

  async updateRegulation(modalityId: string, data: ModalityUpdateRegulation): Promise<ModalityDetail> {
    return apiClient.put<ModalityDetail>(`/modalities/${modalityId}/update-regulation/`, data);
  },
};
