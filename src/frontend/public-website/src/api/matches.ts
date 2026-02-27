import { apiCall, buildQueryString } from './client';

export interface MatchDetail {
  match_id: string;
  location: string;
  status: string;
  start_time: string;
  tournament_id: string;
  tournament_name: string;
  modality_id: string;
  modality_name: string | null;
  participants: Array<Record<string, any>>;
  results: Array<Record<string, any>> | null;
  participant_count: number;
  comment_count: number;
  updated_at: string;
}

export interface MatchDetailList {
  items: MatchDetail[];
  total: number;
  page: number;
  page_size: number;
}

export interface MatchListParams {
  page?: number;
  page_size?: number;
  tournament_id?: string;
  status?: string;
}

export const matchesApi = {
  async getAll(params?: MatchListParams): Promise<MatchDetailList> {
    const queryParams: Record<string, string | undefined> = {
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
      tournament_id: params?.tournament_id,
      status: params?.status,
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<MatchDetailList>(`/matches${queryString}`);
  },

  async getById(matchId: string): Promise<MatchDetail> {
    return apiCall<MatchDetail>(`/matches/${matchId}`);
  },
};
