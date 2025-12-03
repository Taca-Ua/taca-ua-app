import { apiCall, buildQueryString } from './client';
import type { Match } from './types';

export interface GetMatchesParams {
  date?: string;
  date_from?: string;
  date_to?: string;
  modality_id?: string;
  course_id?: string;
  team_id?: string;
  status?: string;
}

export const matchesApi = {
  /**
   * Get matches with optional filters
   */
  getMatches: async (params?: GetMatchesParams): Promise<Match[]> => {
    const query = params ? buildQueryString(params as Record<string, string | undefined>) : '';
    return apiCall<Match[]>(`/calendar/matches${query}`);
  },

  /**
   * Get matches for a specific date
   */
  getMatchesByDate: async (date: string): Promise<Match[]> => {
    return apiCall<Match[]>(`/calendar/matches?date=${date}`);
  },

  /**
   * Get matches for a date range
   */
  getMatchesByDateRange: async (dateFrom: string, dateTo: string): Promise<Match[]> => {
    return apiCall<Match[]>(`/calendar/matches?date_from=${dateFrom}&date_to=${dateTo}`);
  },
};
