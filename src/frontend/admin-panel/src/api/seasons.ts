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
};
