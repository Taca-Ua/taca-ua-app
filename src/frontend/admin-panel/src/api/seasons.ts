import { apiClient } from './client';

export interface Season {
  id: string;
  year: number;
  status: 'draft' | 'active' | 'finished';
  created_at?: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export const seasonsApi = {
  async getAll(): Promise<Season[]> {
    return apiClient.get<Season[]>('/seasons/');
  },

  async create(year: number): Promise<Season> {
    return apiClient.post<Season>('/seasons/', { year });
  },

  async start(seasonId: string): Promise<Season> {
    return apiClient.post<Season>(`/seasons/${seasonId}/start/`, {});
  },

  async finish(seasonId: string): Promise<Season> {
    return apiClient.post<Season>(`/seasons/${seasonId}/finish/`, {});
  },
};
