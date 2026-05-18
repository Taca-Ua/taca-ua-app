import { apiCall } from './client';

export interface SeasonDetail {
  season_id: number;
  name: string;
  is_active: boolean;
}

export interface SeasonList {
    items: SeasonDetail[];
    total: number;
}

export const seasonsApi = {
  async getAll(): Promise<SeasonList> {
    return apiCall<SeasonList>(`/seasons`);
  },

};
