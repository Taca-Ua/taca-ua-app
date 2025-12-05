import { apiClient } from './client';

export interface Modality {
  id: number;
  name: string;
  type: 'coletiva' | 'individual' | 'mista';
  year: string;
  description?: string;
  scoring_schema?: string;
}

export interface ModalityCreate {
  name: string;
  type: 'coletiva' | 'individual' | 'mista';
  year: string;
  description?: string;
  scoring_schema?: string;
}

export interface ModalityUpdate {
  name?: string;
  type?: 'coletiva' | 'individual' | 'mista';
  year?: string;
  description?: string;
  scoring_schema?: string;
}

export const modalitiesApi = {
  async getAll(): Promise<Modality[]> {
    return apiClient.get<Modality[]>('/modalities');
  },

  async getById(modalityId: number): Promise<Modality> {
    return apiClient.get<Modality>(`/modalities/${modalityId}`);
  },

  async create(data: ModalityCreate): Promise<Modality> {
    return apiClient.post<Modality>('/modalities', data);
  },

  async update(modalityId: number, data: ModalityUpdate): Promise<Modality> {
    return apiClient.put<Modality>(`/modalities/${modalityId}`, data);
  },

  async delete(modalityId: number): Promise<void> {
    return apiClient.delete(`/modalities/${modalityId}`);
  },
};
