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
}

export interface GeneralRankingList {
  items: GeneralRanking[];
  total: number;
}

export interface RankingListParams {
  season_id: number;
  nucleo_id?: string;
}

export const rankingApi = {
  async getGeneralRanking(params: RankingListParams): Promise<GeneralRankingList> {
    const queryParams: Record<string, string | undefined> = {
      season_id: params.season_id.toString(),
      nucleo_id: params.nucleo_id,
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<GeneralRankingList>(`/ranking/general${queryString}`);
  },

  async getCourseRanking(courseId: string): Promise<GeneralRanking> {
    return apiCall<GeneralRanking>(`/ranking/general/course/${courseId}`);
  },

  // ==================== Modality Rankings ====================
};

export interface ModalityRanking {
  id: number;
  modality_id: string;
  modality_name: string | null;
  course_id: string;
  course_name: string;
  course_abbreviation: string;
  nucleo_id: string;
  nucleo_name: string;
  nucleo_abbreviation: string;
  points: number;
  rank: number | null;
}

export interface ModalityRankingList {
  items: ModalityRanking[];
  total: number;
}

export interface ModalityRankingListParams {
  modality_id?: string;
  nucleo_id?: string;
}

export const modalityRankingApi = {
  async getModalityRanking(
    params?: ModalityRankingListParams,
  ): Promise<ModalityRankingList> {
    const queryParams: Record<string, string | undefined> = {
      modality_id: params?.modality_id,
      nucleo_id: params?.nucleo_id,
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<ModalityRankingList>(`/ranking/modality${queryString}`);
  },

  async getCourseModalityRankings(courseId: string): Promise<ModalityRanking[]> {
    return apiCall<ModalityRanking[]>(`/ranking/modality/course/${courseId}`);
  },
};
