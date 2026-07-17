import { apiClient } from './client';

export interface GeneralRankingListItem {
  course: {
    id: string;
    name: string;
    logo_url?: string;
  }
  points: number;
  extra_points: number;
}

export interface CourseModalityBreakdownRankingListItem {
  modality: {
    id: string;
    name: string;
  }
  points: number;
}

export interface RankingAmmendment {
  season_id: number;
  course: {
    id: string;
    name: string;
    logo_url?: string;
  }
  modality?: {
    id: string;
    name: string;
  }
  points: number;
  reason?: string;
}

interface RankingAmmendmentCreate {
  course_id: string;
  modality_id?: string;
  points: number;
  reason?: string;
}

interface GetGeneralRankingParams {
  modality_id?: string;
}

export const rankingApi = {
  async getGeneralRanking(seasonId: number, params?: GetGeneralRankingParams): Promise<GeneralRankingListItem[]> {
    return apiClient.get<GeneralRankingListItem[]>(`/ranking/season/${seasonId}/`, params);
  },

  async getCourseModalityBreakdownRanking(seasonId: number, courseId: string): Promise<CourseModalityBreakdownRankingListItem[]> {
    return apiClient.get<CourseModalityBreakdownRankingListItem[]>(`/ranking/season/${seasonId}/course/${courseId}/`);
  },

  async getRankingAmmendments(seasonId: number): Promise<RankingAmmendment[]> {
    return apiClient.get<RankingAmmendment[]>(`/ranking/season/${seasonId}/ammendments/`);
  },

  async createRankingAmmendment(seasonId: number, ammendment: RankingAmmendmentCreate): Promise<RankingAmmendment> {
    return apiClient.post<RankingAmmendment>(`/ranking/season/${seasonId}/ammendments/`, ammendment);
  },
};
