import { apiClient } from './client';

export interface Modality {
  id: string;
  name: string;
  type: 'coletiva' | 'individual' | 'mista';
  scoring_schema?: Record<string, number> | null;
}

export interface ModalityCreate {
  name: string;
  type: 'coletiva' | 'individual' | 'mista';
  scoring_schema?: Record<string, number> | null;
}

export interface ModalityUpdate {
  name?: string;
  type?: 'coletiva' | 'individual' | 'mista';
  scoring_schema?: Record<string, number> | null;
}

export const modalitiesApi = {
  async getAll(): Promise<Modality[]> {
    return apiClient.get<Modality[]>('/modalities');
  },

  async getById(modalityId: string): Promise<Modality> {
    return apiClient.get<Modality>(`/modalities/${modalityId}`);
  },

  async create(data: ModalityCreate): Promise<Modality> {
    return apiClient.post<Modality>('/modalities', data);
  },

  async update(modalityId: string, data: ModalityUpdate): Promise<Modality> {
    return apiClient.put<Modality>(`/modalities/${modalityId}`, data);
  },

  async delete(modalityId: string): Promise<void> {
    return apiClient.delete(`/modalities/${modalityId}`);
  },
};
