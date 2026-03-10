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

export interface ModalityType {
  id: string;
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
  is_playoff: boolean;
  created_at: string;
}

export interface ModalityTypeDetail extends ModalityType {
  // Additional fields can be added here if needed
}

export interface ModalityTypeCreate {
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
  is_playoff: boolean;
}

export interface ModalityTypeUpdate {
  name?: string;
  description?: string;
  escaloes?: EscalaoRow[];
  is_playoff?: boolean;
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

  async getAllMinimal(): Promise<ModalityTypeMinimal[]> {
    return apiClient.get<ModalityTypeMinimal[]>('/modality-types/minimal/');
  }
};
