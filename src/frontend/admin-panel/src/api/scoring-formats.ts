import { apiClient } from './client';

// Types
export interface EscalaoRow {
  escalao: string;
  minParticipants: number | null;
  maxParticipants: number | null;
  points: number[];
}

export interface ScoringFormat {
  id: string;
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
  created_at: string;
  updated_at?: string;
}

export interface ScoringFormatCreate {
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
}

export interface ScoringFormatUpdate {
  name?: string;
  description?: string;
  escaloes?: EscalaoRow[];
}

// API methods
export const scoringFormatsApi = {
  /**
   * Get all scoring formats
   */
  async getAll(): Promise<ScoringFormat[]> {
    return apiClient.get<ScoringFormat[]>('/modality-types');
  },

  /**
   * Get a single scoring format by ID
   */
  async getById(id: string): Promise<ScoringFormat> {
    return apiClient.get<ScoringFormat>(`/modality-types/${id}`);
  },

  /**
   * Create a new scoring format
   */
  async create(data: ScoringFormatCreate): Promise<ScoringFormat> {
    return apiClient.post<ScoringFormat>('/modality-types', data);
  },

  /**
   * Update an existing scoring format
   */
  async update(id: string, data: ScoringFormatUpdate): Promise<ScoringFormat> {
    return apiClient.put<ScoringFormat>(`/modality-types/${id}`, data);
  },

  /**
   * Delete a scoring format
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/modality-types/${id}`);
  },
};
