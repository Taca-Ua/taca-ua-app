import keycloak from '../lib/keycloak';
import { apiClient } from './client2';

// Helper types
export interface MatchLineup {
  participant_id: string;
  lineup: {
    player_id: string;
    name: string;
    is_starter: boolean;
    jersey_number?: number;
  }[];
}

// Response types
export interface MatchListItem {
  id: string;
  tournament_id: string;
  location: string;
  start_time: string;
  status: string;
  participants: {
    id: string;
    name: string;
    score?: number;
    position?: number;
  }[];
};

export interface MatchDetail extends MatchListItem {
  comments: {
    id: string;
    message: string;
  }[];
  lineups: MatchLineup[];
}

// Request types
export interface MatchListFilter {
  tournament_id?: string;
  status?: string;
}

export interface MatchCreate {
  tournament_id: string;
  location: string;
  start_time: string;
  participants: string[];
}

export interface MatchUpdate {
  location?: string;
  start_time?: string;
  status?: string;
}

export interface MatchPublishResults {
  participant_results: {
    participant_id: string;
    score?: number;
    position?: number;
  }[];
  status?: 'in_progress' | 'finished';
}

export interface CommentCreate {
  message: string;
}

export interface LineupAssign {
  participant: string;
  players: string[];
}

export const matchesApi = {
  async getAll(params?: MatchListFilter): Promise<MatchListItem[]> {
    return apiClient.get<MatchListItem[]>('/matches/', params );
  },

  async create(data: MatchCreate): Promise<MatchListItem> {
    return apiClient.post<MatchListItem>('/matches/', data);
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

  async publishResults(matchId: string, data: MatchPublishResults): Promise<MatchDetail> {
    return apiClient.post<MatchDetail>(`/matches/${matchId}/results/`, data);
  },

  async assignLineup(matchId: string, data: LineupAssign): Promise<JSON> {
    return apiClient.post<JSON>(`/matches/${matchId}/lineup/`, data);
  },

  async addComment(matchId: string, data: CommentCreate): Promise<MatchDetail> {
    return apiClient.post<MatchDetail>(`/matches/${matchId}/comments/`, data);
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

    const response = await fetch(`/api/admin/matches/${matchId}/sheet/`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!response.ok) {
      throw new Error('Failed to download match sheet');
    }

    return response.blob();
  },

  async getMatchTeamSheet(matchId: string, teamId: string): Promise<Blob> {
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

    const response = await fetch(`/api/admin/matches/${matchId}/team/${teamId}/sheet/`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!response.ok) {
      throw new Error('Failed to download match team sheet');
    }

    return response.blob();
  },
};
