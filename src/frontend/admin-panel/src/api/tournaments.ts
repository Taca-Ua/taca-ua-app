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
    id: string;
    name: string;
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
  format?: string;
  rank?: {
    name: string;
    points: number[];
  };
  format_data?: Record<string, any>;

  qualification_slots?: {
    tournament: TournamentListItem;
    starting_position: number;
    ending_position: number;
  }[];
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
  course_id?: string;
  team_id?: string;
};

export interface TournamentCreate {
  name: string;
  modality_id: string;
  start_date?: string;
  season_id?: number;
  scoring_format_id?: string;

  format?: string;
  format_data?: Record<string, any>;

  competitor_rules?: {
    tournament_id: string;
    starting_position: number;
    ending_position: number;
  }[];
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

  async addCompetitors(id: string, entity_ids: string[]): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/add-competitors/`, {entity_ids} );
  },

  async removeCompetitors(id: string, competitor_ids: string[]): Promise<TournamentDetail> {
    return apiClient.put<TournamentDetail>(`/tournaments/${id}/remove-competitors/`, {competitor_ids});
  },

  async getStandings(id: string): Promise<TournamentStandingsEntry[]> {
    return apiClient.get<TournamentStandingsEntry[]>(`/tournaments/${id}/standings/`);
  },

  async getFormatDetails(id: string): Promise<Record<string, any>> {
    return apiClient.get<Record<string, any>>(`/tournaments/${id}/format/`);
  },

  async updateFormatMeta(id: string, format_meta: Record<string, any>): Promise<Record<string, any>> {
    return apiClient.put<Record<string, any>>(`/tournaments/${id}/format/`, format_meta);
  }
};
