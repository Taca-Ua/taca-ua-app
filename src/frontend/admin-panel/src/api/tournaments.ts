import { apiClient } from './client';
import { type Match } from "./matches";
import type { Modality } from './modalities';
import type { Team } from './teams';

export interface Tournament {
  id: string;
  name: string;
  status: string;
}

export interface TournamentDetail extends Tournament {
  modality: Modality;
  start_date: string;
  teams: Team[];
  matches: Match[];
}

export interface TournamentCreate {
  name: string;
  modality_id: string;
  teams_ids?: string[];
  start_date?: string;
}

export interface TournamentUpdate {
  name?: string;
  start_date?: string;
  status?: 'draft' | 'active' | 'finished';
  teams_add?: string[];
  teams_remove?: string[];
}

// Input interfaces
export interface TournamentFinish {
  ranking_entries?: { team_id: string; position: number }[];
}

export const tournamentsApi = {
  async getAll(): Promise<Tournament[]> {
    return apiClient.get<Tournament[]>('/tournaments/');
  },

  async create(data: TournamentCreate): Promise<Tournament> {
    return apiClient.post<Tournament>('/tournaments/', data);
  },

  async getById(id: string): Promise<TournamentDetail> {
    return apiClient.get<TournamentDetail>(`/tournaments/${id}/`);
  },

  async update(id: string, data: TournamentUpdate): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/`, data);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/tournaments/${id}/`);
  },

  async finish(id: string, data: TournamentFinish): Promise<TournamentDetail> {
    return apiClient.post<TournamentDetail>(`/tournaments/${id}/finish/`, data);
  },
};
