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
};
