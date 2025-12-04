import { apiClient } from './client';

export interface Modality {
  id: number;
  name: string;
  type: string;
  description?: string;
}

export const modalitiesApi = {
  async getAll(): Promise<Modality[]> {
    return apiClient.get<Modality[]>('/modalities');
  },

  async getById(modalityId: number): Promise<Modality> {
    return apiClient.get<Modality>(`/modalities/${modalityId}`);
  },
};
