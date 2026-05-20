import { apiClient } from './client';

// Choices
type tournamentStatusChoices = 'draft' | 'active' | 'finished';
type tournamentCompetitorTypeChoices = 'team' | 'athlete';

// Response interfaces
export interface TournamentListItem {
  id: string;
  name: string;
  status: tournamentStatusChoices;
  modality: {
    id: string;
    name: string;
  };
  start_date?: string;
}

export interface TournamentDetail extends TournamentListItem {
  competitor_type: tournamentCompetitorTypeChoices;
  competitors: {
    id: string;
    entity_id: string;
    name: string;
    course_name: string;
  }[];
  scoring_format: {
    name: string;
    rank: string;
    points: number[];
  };
  season: {
    id: number;
    name: string;
  };
  standings?: {
    position: number;
    competitor_id: string;
  }[];
  rounds: number[];
  format: string;
  format_data?: Record<string, any>;
}

export interface TournamentStandingsEntry {
  competitor_id: string;
  competitor_name: string;
  position: number;
  format_meta: Record<string, any>;
}

// Input interfaces
export interface TournamentListParams {
  status?: tournamentStatusChoices;
  modality_id?: string;
  season_id?: number;
};

export interface TournamentCreate {
  name: string;
  modality_id: string;
  start_date?: string;
  season_id?: number;
  scoring_format_id?: string;

  format?: string;
  format_data?: Record<string, any>;
};

export interface TournamentUpdate {
  name?: string;
  start_date?: string;
  status?: tournamentStatusChoices;
  is_playoff?: boolean;
};

export interface TournamentFinish {
  ranking_entries: {
    position: number;
    competitor_id: string;
  }[];
};

export interface TournamentCompetitorsAddEntry {
  competitor_type: tournamentCompetitorTypeChoices;
  entity_id: string;
};

export interface TournamentCompetitorsDelete {
  competitors_ids: string[];
}

export const tournamentsApi = {
  async getAll(params?: TournamentListParams): Promise<TournamentListItem[]> {
    return apiClient.get<TournamentListItem[]>('/tournaments/', params );
  },

  async create(data: TournamentCreate): Promise<TournamentListItem> {
    return apiClient.post<TournamentListItem>('/tournaments/', data);
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

  async addCompetitors(id: string, competitors: TournamentCompetitorsAddEntry[]): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/competitors/add/`, competitors );
  },

  async removeCompetitors(id: string, competitors_ids: TournamentCompetitorsDelete): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/competitors/remove/`, competitors_ids);
  },

  async getRounds(id: string): Promise<number[]> {
    return apiClient.get<number[]>(`/tournaments/${id}/rounds/`);
  },

  async getStandings(id: string): Promise<TournamentStandingsEntry[]> {
    return apiClient.get<TournamentStandingsEntry[]>(`/tournaments/${id}/standings/`);
  },

  async updateFormatMeta(id: string, format_meta: Record<string, any>): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/format-meta/`, { format_meta });
  }
};
