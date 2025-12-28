import { apiCall, buildQueryString } from './client';
import type { Regulation } from './types';

export const regulationsApi = {
  /**
   * Get all regulations
   */
  getRegulations: async (category?: string): Promise<Regulation[]> => {
    const query = category ? buildQueryString({ category }) : '';
    return apiCall<Regulation[]>(`/regulations${query}`);
  },

  /**
   * Get a specific regulation by ID
   */
  getRegulation: async (regulationId: string): Promise<Regulation> => {
    return apiCall<Regulation>(`/regulations/${regulationId}`);
  },
};
