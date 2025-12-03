import { apiCall, buildQueryString } from './client';
import type { ModalityRanking, GeneralRankingResponse } from './types';

export const rankingsApi = {
  /**
   * Get general ranking (all courses)
   */
  getGeneralRanking: async (seasonId?: string): Promise<GeneralRankingResponse> => {
    const query = seasonId ? buildQueryString({ season_id: seasonId }) : '';
    return apiCall<GeneralRankingResponse>(`/rankings/general${query}`);
  },

  /**
   * Get modality ranking
   */
  getModalityRanking: async (modalityId: string, seasonId?: string): Promise<ModalityRanking> => {
    const query = seasonId ? buildQueryString({ season_id: seasonId }) : '';
    return apiCall<ModalityRanking>(`/rankings/modality/${modalityId}${query}`);
  },

  /**
   * Get course ranking (breakdown by modality)
   */
  getCourseRanking: async (courseId: string, seasonId?: string): Promise<{ [modalityName: string]: number }> => {
    const query = seasonId ? buildQueryString({ season_id: seasonId }) : '';
    return apiCall<{ [modalityName: string]: number }>(`/rankings/course/${courseId}${query}`);
  },
};
