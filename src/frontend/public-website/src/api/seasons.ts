import { apiCall } from './client';

export interface Season {
  season_id: string;
  year: number;
  status: 'draft' | 'active' | 'finished';
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export const seasonsApi = {
  async getAll(): Promise<Season[]> {
    return apiCall<Season[]>('/seasons');
  },
};
