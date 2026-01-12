import { apiClient } from './client';

// Types
export interface EscalaoRow {
  escalao: string;
  minParticipants: number | null;
  maxParticipants: number | null;
  points: number[];
}

export interface ModalityType {
  id: string;
  name: string;
}

export interface ModalityTypeDetail extends ModalityType {
  description?: string;
  escaloes: EscalaoRow[];
  created_at: string;
}

export interface ModalityTypeCreate {
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
}

export interface ModalityTypeUpdate {
  name?: string;
  description?: string;
  escaloes?: EscalaoRow[];
}

// API methods
export const modalityTypesApi = {
  async getAll(): Promise<ModalityType[]> {
    return apiClient.get<ModalityType[]>('/modality-types/');
  },

  async create(data: ModalityTypeCreate): Promise<ModalityType> {
    return apiClient.post<ModalityType>('/modality-types/', data);
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
