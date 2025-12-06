import { apiClient } from './client';

export interface Tournament {
  id: number;
  name: string;
  modality_id: number;
  season_id: number;
  season_year?: string;
  rules?: string;
  status: 'draft' | 'active' | 'finished';
  start_date?: string;
  teams?: number[];
}

export interface TournamentCreate {
  name: string;
  modality_id: number;
  season_id: number;
  season_year?: string;
  rules?: string;
  teams?: number[];
  start_date?: string;
}

export interface TournamentUpdate {
  name?: string;
  rules?: string;
  teams?: number[];
  start_date?: string;
  status?: 'draft' | 'active' | 'finished';
}

export const tournamentsApi = {
  async getAll(): Promise<Tournament[]> {
    return apiClient.get<Tournament[]>('/tournaments');
  },

  async getById(id: number): Promise<Tournament> {
    return apiClient.get<Tournament>(`/tournaments/${id}`);
  },

  async create(data: TournamentCreate): Promise<Tournament> {
    return apiClient.post<Tournament>('/tournaments', data);
  },

  async update(id: number, data: TournamentUpdate): Promise<Tournament> {
    return apiClient.put<Tournament>(`/tournaments/${id}`, data);
  },

  async delete(id: number): Promise<void> {
    return apiClient.delete(`/tournaments/${id}`);
  },

  async finish(id: number): Promise<Tournament> {
    return apiClient.post<Tournament>(`/tournaments/${id}/finish`, {});
  },
};
