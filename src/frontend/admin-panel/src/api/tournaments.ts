import { apiClient } from './client';
import { type Match } from "./matches";

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
	matches: Match[];
    ranking_positions?: number; // Number of ranking positions to collect (e.g., 3 for top 3)
    final_rankings?: {
        team_id: string;
        team_name: string;
        position: number;
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

  async finish(id: string, rankings?: { team_id: string; position: number }[]): Promise<TournamentDetail> {
    return apiClient.post<TournamentDetail>(`/tournaments/${id}/finish`, { "ranking_entries": rankings  });
  },
};
