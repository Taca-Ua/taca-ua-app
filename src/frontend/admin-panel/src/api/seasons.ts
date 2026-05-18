import { apiClient } from './client';

export interface SeasonListItem {
  id: number;
  name: string;
}

export interface SeasonDetail extends SeasonListItem {

}

export interface SeasonCreateRequest {
  name: string;
}

export interface SeasonSummary {
  id: number;
  name: string;

  modality_types_count: number;
  active_modalities_count: number;
  active_courses_count: number;
  teams_count: number;

  tournaments_summary: {
    finished: number;
    ongoing: number;
    scheduled: number;
  };

  matches_summary: {
    finished: number;
    ongoing: number;
    scheduled: number;
  };

  members_summary: {
    athletes: number;
    staff: number;
  };
}

export const seasonsApi = {
  async getAll(): Promise<SeasonListItem[]> {
    return apiClient.get<SeasonListItem[]>('/seasons/');
  },

  async createSeason(seasonData: SeasonCreateRequest): Promise<SeasonListItem> {
    return apiClient.post<SeasonListItem>('/seasons/', seasonData);
  },

  async getCurrent(): Promise<SeasonDetail> {
    return apiClient.get<SeasonDetail>('/seasons/current/');
  },

  async getSeasonSummary(seasonId?: number): Promise<SeasonSummary> {
    let params = {};
    if (seasonId) {
      params = { ...params, season_id: seasonId };
    }

    return apiClient.get<SeasonSummary>(`/seasons/summary/`, params );
  },
};
