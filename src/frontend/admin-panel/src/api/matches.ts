import { apiClient } from './client';

interface Lineup {
	player_id: string;
	jersey_number: number;
	is_starter: boolean;
}

export interface Match {
  id: string;
  tournament_id: string;
  team_home_name: string;
  team_away_name: string;
  team_home_id: string;
  team_away_id: string;
  team_home: { id: string; name: string; lineup: Lineup[] };
  team_away: { id: string; name: string; lineup: Lineup[] };
  location: string;
  start_time: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score: number | null;
  away_score: number | null;
}

export interface MatchCreate {
  tournament_id: string;
  team_home_id: string;
  team_away_id: string;
  location: string;
  start_time: string;
}

export interface MatchUpdate {
  team_home_id?: string;
  team_away_id?: string;
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
  team_id: string;
  players: Lineup[];
}

export interface MatchComment {
  message: string;
}

export const matchesApi = {
  async getAll(): Promise<Match[]> {
    return apiClient.get<Match[]>('/matches');
  },

  async getById(matchId: string): Promise<Match> {
    return apiClient.get<Match>(`/matches/${matchId}`);
  },

  async create(data: MatchCreate): Promise<Match> {
    return apiClient.post<Match>('/matches', data);
  },

  async update(matchId: string, data: MatchUpdate): Promise<Match> {
    return apiClient.put<Match>(`/matches/${matchId}`, data);
  },

  async delete(matchId: string): Promise<void> {
    return apiClient.delete(`/matches/${matchId}`);
  },

  async submitResult(matchId: string, data: MatchResult): Promise<Match> {
    return apiClient.post<Match>(`/matches/${matchId}/result`, data);
  },

  async submitLineup(matchId: string, data: MatchLineup): Promise<void> {
    return apiClient.post<void>(`/matches/${matchId}/lineup`, data);
  },

  async addComment(matchId: string, data: MatchComment): Promise<void> {
    return apiClient.post<void>(`/matches/${matchId}/comments`, data);
  },

  async getMatchSheet(matchId: string): Promise<Blob> {
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
