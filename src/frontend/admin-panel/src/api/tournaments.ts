import { apiClient } from './client';

export interface Tournament {
  id: number;
  name: string;
  modality_id: number;
  modality_name: string;
  season_id: number;
  season_name: string;
  start_date: string;
  end_date: string;
  status: 'upcoming' | 'active' | 'finished';
  description?: string;
}

export const tournamentsApi = {
  async getAll(): Promise<Tournament[]> {
    return apiClient.get<Tournament[]>('/tournaments');
  },

  async getById(tournamentId: number): Promise<Tournament> {
    return apiClient.get<Tournament>(`/tournaments/${tournamentId}`);
  },
};
