import { apiClient } from './client';

export interface Season {
  id: number;
  year: number;
  status: 'draft' | 'active' | 'finished';
}

export const seasonsApi = {
  async getAll(): Promise<Season[]> {
    return apiClient.get<Season[]>('/seasons');
  },

  async start(seasonId: number): Promise<Season> {
    return apiClient.post<Season>(`/seasons/${seasonId}/start`, {});
  },

  async finish(seasonId: number): Promise<Season> {
    return apiClient.post<Season>(`/seasons/${seasonId}/finish`, {});
  },
};
