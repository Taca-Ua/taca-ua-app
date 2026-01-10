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
  /**
   * Get all modality types
   */
  async getAll(): Promise<ModalityType[]> {
    return apiClient.get<ModalityType[]>('/modality-types/');
  },

  /**
   * Create a new modality type
   */
  async create(data: ModalityTypeCreate): Promise<ModalityTypeDetail> {
    return apiClient.post<ModalityTypeDetail>('/modality-types/', data);
  },

  /**
   * Get all modality types in simplified form (id and name only)
   */
  async getAllSimplified(): Promise<ModalityType[]> {
	return apiClient.get<ModalityType[]>('/modality-types/simple/');
  },

  /**
   * Get a single modality type by ID
   */
  async getById(id: string): Promise<ModalityTypeDetail> {
    return apiClient.get<ModalityTypeDetail>(`/modality-types/${id}/`);
  },

  /**
   * Update an existing modality type
   */
  async update(id: string, data: ModalityTypeUpdate): Promise<ModalityTypeDetail> {
    return apiClient.put<ModalityTypeDetail>(`/modality-types/${id}/`, data);
  },

  /**
   * Delete a modality type
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/modality-types/${id}/`);
  },
};
