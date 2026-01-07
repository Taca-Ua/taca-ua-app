import { apiClient } from './client';

export interface Modality {
  id: string;
  name: string;
  modality_type_name: string;
}

export interface ModalityDetail {
  id: string;
  name: string;
  modality_type_id: string;
  modality_type_name: string;
}

export interface ModalityCreate {
  name: string;
  modality_type_id: string;
}

export interface ModalityUpdate {
  name?: string;
  modality_type_id?: string;
}

export const modalitiesApi = {
  async getAll(): Promise<Modality[]> {
    return apiClient.get<Modality[]>('/modalities/');
  },

  async create(data: ModalityCreate): Promise<Modality> {
    return apiClient.post<Modality>('/modalities/', data);
  },

  async getById(modalityId: string): Promise<ModalityDetail> {
    return apiClient.get<ModalityDetail>(`/modalities/${modalityId}/`);
  },

  async update(modalityId: string, data: ModalityUpdate): Promise<ModalityDetail> {
    return apiClient.put<ModalityDetail>(`/modalities/${modalityId}/`, data);
  },

  async delete(modalityId: string): Promise<void> {
    return apiClient.delete(`/modalities/${modalityId}/`);
  },
};
