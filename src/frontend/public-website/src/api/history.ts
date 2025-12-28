import { apiCall } from './client';
import type { HistoricalWinner } from './types';

export const historyApi = {
  /**
   * Get historical winners by season
   */
  getHistoricalWinners: async (): Promise<HistoricalWinner[]> => {
    return apiCall<HistoricalWinner[]>('/history/winners');
  },
};
