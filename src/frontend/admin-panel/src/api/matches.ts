import { apiClient } from './client';
import { type Team } from './teams';
import { type Student } from './members';

interface Participant {
  participant_type: string;
  team?: Team;
  athlete?: Student;
}
export interface Match {
  id: string;
  participants: Participant[];
  location: string;
  start_time: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score: number | null;
  away_score: number | null;
}

interface TeamWithLineup extends Team {
  players: Student[];
}

export interface MatchDetail extends Match {
  team_home: TeamWithLineup;
  team_away: TeamWithLineup;
  additional_info?: JSON;
}

export interface MatchCreate {
  tournament_id: string;
  team_home_id: string;
  team_away_id: string;
  location: string;
  start_time: string;
}

export interface MatchUpdate {
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

interface PlayerLineup {
  player_id: string;
  jersey_number: number;
  is_starter: boolean;
}
export interface MatchLineup {
  team_id: string;
  players: PlayerLineup[];
}

export interface MatchComment {
  message: string;
}

export const matchesApi = {
  async getAll(): Promise<Match[]> {
    return apiClient.get<Match[]>('/matches/');
  },

  async create(data: MatchCreate): Promise<Match> {
    return apiClient.post<Match>('/matches/', data);
  },

  async getById(matchId: string): Promise<MatchDetail> {
    return apiClient.get<MatchDetail>(`/matches/${matchId}/`);
  },

  async update(matchId: string, data: MatchUpdate): Promise<MatchDetail> {
    return apiClient.put<MatchDetail>(`/matches/${matchId}/`, data);
  },

  async delete(matchId: string): Promise<void> {
    return apiClient.delete(`/matches/${matchId}/`);
  },

  async submitResult(matchId: string, data: MatchResult): Promise<Match> {
    return apiClient.post<Match>(`/matches/${matchId}/result/`, data);
  },

  async submitLineup(matchId: string, data: MatchLineup): Promise<void> {
    return apiClient.post<void>(`/matches/${matchId}/lineup/`, data);
  },

  async addComment(matchId: string, data: MatchComment): Promise<void> {
    return apiClient.post<void>(`/matches/${matchId}/comments/`, data);
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
