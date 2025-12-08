import { apiClient } from './client';

export interface Match {
  id: number;
  tournament_id: number;
  team_home_id: number;
  team_away_id: number;
  location: string;
  start_time: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score: number | null;
  away_score: number | null;
}

export interface MatchCreate {
  tournament_id: number;
  team_home_id: number;
  team_away_id: number;
  location: string;
  start_time: string;
}

export interface MatchUpdate {
  team_home_id?: number;
  team_away_id?: number;
  location?: string;
  start_time?: string;
  status?: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score?: number | null;
  away_score?: number | null;
}

export interface MatchResult {
  home_score: number;
  away_score: number;
}

export interface MatchLineup {
  team_id: number;
  players: number[];
}

export interface MatchComment {
  message: string;
}

export const matchesApi = {
  async getAll(): Promise<Match[]> {
    return apiClient.get<Match[]>('/matches');
  },

  async getById(matchId: number): Promise<Match> {
    return apiClient.get<Match>(`/matches/${matchId}`);
  },

  async create(data: MatchCreate): Promise<Match> {
    return apiClient.post<Match>('/matches', data);
  },

  async update(matchId: number, data: MatchUpdate): Promise<Match> {
    return apiClient.put<Match>(`/matches/${matchId}`, data);
  },

  async delete(matchId: number): Promise<void> {
    return apiClient.delete(`/matches/${matchId}`);
  },

  async submitResult(matchId: number, data: MatchResult): Promise<Match> {
    return apiClient.post<Match>(`/matches/${matchId}/result`, data);
  },

  async submitLineup(matchId: number, data: MatchLineup): Promise<void> {
    return apiClient.post<void>(`/matches/${matchId}/lineup`, data);
  },

  async addComment(matchId: number, data: MatchComment): Promise<void> {
    return apiClient.post<void>(`/matches/${matchId}/comments`, data);
  },

  async getMatchSheet(matchId: number): Promise<Blob> {
    const response = await fetch(`/api/admin/matches/${matchId}/sheet`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to download match sheet');
    }

    return response.blob();
  },
};
