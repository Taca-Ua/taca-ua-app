import { apiClient } from './client';

// Types
export interface EscalaoRow {
  escalao: string;
  minParticipants: number | null;
  maxParticipants: number | null;
  points: number[];
}

export interface ModalityTypeMinimal {
  id: string;
  name: string;
}

export interface ModalityTypeListItem {
  id: string;
  name: string;
  description?: string;
  is_playoff: boolean;
  tournament_competitor_type: 'individual' | 'team';
  num_escaloes: number;
}

export interface ModalityTypeDetail extends ModalityTypeListItem {
  escaloes: EscalaoRow[];
}

export interface ModalityTypeCreate {
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
  is_playoff?: boolean;
  tournament_competitor_type: 'individual' | 'team';
  season_id?: number;
}

export interface ModalityTypeUpdate {
  name?: string;
  description?: string;
  escaloes?: EscalaoRow[];
  is_playoff?: boolean;
  tournament_competitor_type?: 'individual' | 'team';
}

export interface ModalityTypeListParameters {
  season_id?: number;
}

// API methods
export const modalityTypesApi = {
  async getAll(params?: ModalityTypeListParameters): Promise<ModalityTypeListItem[]> {
    return apiClient.get<ModalityTypeListItem[]>('/modality-types/', params);
  },

  async create(data: ModalityTypeCreate): Promise<ModalityTypeListItem> {
    return apiClient.post<ModalityTypeListItem>('/modality-types/', data);
  },

  async getAllMinimal(): Promise<ModalityTypeMinimal[]> {
    return apiClient.get<ModalityTypeMinimal[]>('/modality-types/minimal/');
  },

  async getById(id: string): Promise<ModalityTypeDetail> {
    return apiClient.get<ModalityTypeDetail>(`/modality-types/${id}/`);
  },

  async update(id: string, data: ModalityTypeUpdate): Promise<ModalityTypeDetail> {
    return apiClient.put<ModalityTypeDetail>(`/modality-types/${id}/`, data);
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/modality-types/${id}/`);
  },
};
