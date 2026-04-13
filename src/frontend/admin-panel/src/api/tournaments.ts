import { apiClient } from './client';
import { type Match } from "./matches";
import type { Modality } from './modalities';
import type { Team } from './teams';
import type { Student } from './members';
import type { ModalityType } from "./modality-types";

export interface TournamentCompetitor {
  competitor_type: 'team' | 'athlete';
  team_id?: string;
  athlete_id?: string;
}

export interface TournamentCompetitorDetail {
  id: string;
  competitor_type: 'team' | 'athlete';
  team: Team;
  athlete: Student;
}

export interface Tournament {
  id: string;
  name: string;
  status: string;
  modality: Modality;
  start_date?: string;
  season_id?: string;
}

export interface TournamentDetail extends Tournament {
  start_date: string;
  scoring_format: ModalityType;
  competitors: TournamentCompetitorDetail[];
  matches: Match[];
  competitor_type: 'team' | 'athlete';
}

export interface TournamentCreate {
  name: string;
  modality_id: string;
  is_playoff?: boolean;
  competitors: TournamentCompetitor[];
  start_date?: string;
  season_id?: string;
}

export interface TournamentUpdate {
  name?: string;
  start_date?: string;
  status?: 'draft' | 'active' | 'finished';
  competitors_add?: TournamentCompetitor[];
  competitors_remove?: TournamentCompetitor[];
  is_playoff?: boolean;
}

// Input interfaces
interface TournamentFinishEntry extends TournamentCompetitor {
  position: number;
}

export interface TournamentFinish {
  ranking_entries?: TournamentFinishEntry[];
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

  async addCompetitors(id: string, competitors: TournamentCompetitor[]): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/competitors/add/`, competitors );
  },

  async removeCompetitors(id: string, competitors_ids: string[]): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/competitors/remove/`, { competitors_ids });
  }
};
