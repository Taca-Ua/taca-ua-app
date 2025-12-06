import { apiCall } from './client';
import type { Season } from './types';

export const seasonsApi = {
  /**
   * Get all seasons
   */
  getSeasons: async (): Promise<Season[]> => {
    return apiCall<Season[]>('/seasons');
  },

  /**
   * Get active season
   */
  getActiveSeason: async (): Promise<Season | null> => {
    const seasons = await apiCall<Season[]>('/seasons');
    return seasons.find(s => s.status === 'active') || null;
  },
};
