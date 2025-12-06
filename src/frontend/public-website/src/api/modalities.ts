import { apiCall } from './client';
import type { Modality } from './types';

export const modalitiesApi = {
  /**
   * Get all modalities
   */
  getModalities: async (): Promise<Modality[]> => {
    return apiCall<Modality[]>('/modalities');
  },

  /**
   * Get a specific modality by ID
   */
  getModality: async (modalityId: number): Promise<Modality> => {
    return apiCall<Modality>(`/modalities/${modalityId}`);
  },
};
