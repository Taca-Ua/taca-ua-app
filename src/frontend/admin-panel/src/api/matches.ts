import keycloak from '../lib/keycloak';
import { apiClient } from './client';
import { type Team } from './teams';
import { type Student } from './members';

// Participant interfaces
export interface ParticipantDetail {
  id: string;
  participant_type: string;
  team?: Team;
  athlete?: Student;
  score?: number;
  position?: number;
}

export interface ParticipantCreate {
  participant_type: string;
  team_id?: string;
  athlete_id?: string;
}

// Match interfaces
export interface Match {
  id: string;
  tournament_id: string;
  location: string;
  start_time: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  created_at: string;
  participants: ParticipantDetail[];
}

export interface MatchDetail {
  id: string;
  tournament_id: string;
  location: string;
  start_time: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  created_by: string;
  created_at: string;
  updated_at: string;
  participants: ParticipantDetail[];
}

export interface MatchCreate {
  tournament_id: string;
  location: string;
  start_time: string;
  participants: ParticipantCreate[];
}

export interface MatchUpdate {
  location?: string;
  start_time?: string;
  status?: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
}

// Result interfaces
export interface ParticipantResult {
  participant_id: string;
  score?: number;
  position?: number;
  result_details?: JSON;
}
export interface MatchResultsUpdate {
  participant_results: ParticipantResult[];
  status?: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
}

// Lineup interfaces
export interface PlayerLineup {
  player_id: string;
  jersey_number: number;
  is_starter: boolean;
}
export interface LineupAssign {
  team_id: string;
  players: PlayerLineup[];
}
export interface LineupDetail {
  id: string;
  match_id: string;
  team_id: string;
  player_id: string;
  player?: Student;
  jersey_number: number;
  is_starter: boolean;
  created_at: string;
}

// Comment interfaces
export interface CommentCreate {
  message: string;
}
export interface CommentDetail {
  id: string;
  match_id: string;
  message: string;
  created_by: string;
  created_at: string;
}

export const matchesApi = {
  async getAll(): Promise<Match[]> {
    return apiClient.get<Match[]>('/matches/');
  },

  async create(data: MatchCreate): Promise<MatchDetail> {
    return apiClient.post<MatchDetail>('/matches/', data);
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

  async addParticipants(matchId: string, data: ParticipantCreate[]): Promise<ParticipantDetail[]> {
    return apiClient.post<ParticipantDetail[]>(`/matches/${matchId}/participants/`, data);
  },

  async removeParticipant(matchId: string, participantId: string): Promise<void> {
    return apiClient.delete(`/matches/${matchId}/participants/${participantId}/`);
  },

  async updateMatchResults(matchId: string, data: MatchResultsUpdate): Promise<MatchDetail> {
    return apiClient.put<MatchDetail>(`/matches/${matchId}/results/`, data);
  },

  async getLineups(matchId: string): Promise<LineupDetail[]> {
    return apiClient.get<LineupDetail[]>(`/matches/${matchId}/lineup/`);
  },

  async assignLineup(matchId: string, data: LineupAssign): Promise<JSON> {
    return apiClient.post<JSON>(`/matches/${matchId}/lineup/`, data);
  },

  async getComments(matchId: string): Promise<CommentDetail[]> {
    return apiClient.get<CommentDetail[]>(`/matches/${matchId}/comments/`);
  },

  async addComment(matchId: string, data: CommentCreate): Promise<CommentDetail> {
    return apiClient.post<CommentDetail>(`/matches/${matchId}/comments/`, data);
  },

  async deleteComment(matchId: string, commentId: string): Promise<void> {
    return apiClient.delete(`/matches/${matchId}/comments/${commentId}/`);
  },

  async getMatchSheet(matchId: string): Promise<Blob> {
    let token = keycloak.token ?? null;
    if (keycloak.authenticated) {
      try {
        await keycloak.updateToken(30);
        token = keycloak.token ?? null;
      } catch {
        keycloak.login();
        throw new Error('Session expired, please log in again');
      }
    }

    const response = await fetch(`/api/admin/matches/${matchId}/sheet`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!response.ok) {
      throw new Error('Failed to download match sheet');
    }

    return response.blob();
  },
};
