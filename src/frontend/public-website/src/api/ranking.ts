import { apiCall, buildQueryString } from './client';

export interface GeneralRanking {
  id: number;
  course_id: string;
  course_name: string;
  course_abbreviation: string;
  nucleo_id: string;
  nucleo_name: string;
  nucleo_abbreviation: string;
  points: number;
  rank: number | null;
  tournaments_participated: number;
  updated_at: string;
}

export interface GeneralRankingList {
  items: GeneralRanking[];
  total: number;
}

export interface RankingListParams {
  nucleo_id?: string;
}

export const rankingApi = {
  async getGeneralRanking(params?: RankingListParams): Promise<GeneralRankingList> {
    const queryParams: Record<string, string | undefined> = {
      nucleo_id: params?.nucleo_id,
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<GeneralRankingList>(`/ranking/general${queryString}`);
  },

  async getCourseRanking(courseId: string): Promise<GeneralRanking> {
    return apiCall<GeneralRanking>(`/ranking/general/course/${courseId}`);
  },
};
