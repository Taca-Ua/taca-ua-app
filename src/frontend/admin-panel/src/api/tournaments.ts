import { apiClient } from './client';

export interface Tournament {
  id: string;
  modality_name: string;
  name: string;
  status: string;
  start_date?: string;
}

export interface TournamentDetail extends Tournament {
    teams: {
        id: string;
        name: string;
    }[];
}

export interface TournamentCreate {
    modality_id: string;
    name: string;
    teams?: string[];
    start_date?: string;
}

export interface TournamentUpdate {
    name?: string;
    start_date?: string;
    status?: 'draft' | 'active' | 'finished';
    teams_add?: string[];
    teams_remove?: string[];
}

export const tournamentsApi = {
  async getAll(): Promise<Tournament[]> {
    return apiClient.get<Tournament[]>('/tournaments');
  },

  async getById(id: string): Promise<TournamentDetail> {
    return apiClient.get<TournamentDetail>(`/tournaments/${id}`);
  },

  async create(data: TournamentCreate): Promise<TournamentDetail> {
    return apiClient.post<TournamentDetail>('/tournaments', data);
  },

  async update(id: string, data: TournamentUpdate): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}`, data);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/tournaments/${id}`);
  },

  async finish(id: string): Promise<TournamentDetail> {
    return apiClient.post<TournamentDetail>(`/tournaments/${id}/finish`, {});
  },
};
