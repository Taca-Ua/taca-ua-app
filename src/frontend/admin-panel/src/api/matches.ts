import { apiClient } from './client';

// Helper types
export interface MatchLineup {
  participant_id: string;
  lineup: {
    player_id: string;
    player_name: string;
    player_course: string;
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
  journey?: number;
  participants: {
    id: string;
    entity_id: string;
    name: string;
    score?: number;
    position?: number;
  }[];
};

export interface MatchDetail extends MatchListItem {
  comments: {
    id: string;
    message: string;
    author_name: string;
    can_edit: boolean;
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

export interface LineupUpdate {
  participant: string;
  players: {
    player_id: string;
    is_starter: boolean;
    jersey_number?: number | null;
  }[];
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

  async assignLineup(matchId: string, data: LineupAssign): Promise<MatchDetail> {
    return apiClient.post<MatchDetail>(`/matches/${matchId}/lineups/`, data);
  },

  async updateLineup(matchId: string, data: LineupUpdate): Promise<MatchDetail> {
    return apiClient.put<MatchDetail>(`/matches/${matchId}/lineups/`, data);
  },

  async addComment(matchId: string, data: CommentCreate): Promise<MatchDetail> {
    return apiClient.post<MatchDetail>(`/matches/${matchId}/comments/`, data);
  },

  async deleteComment(matchId: string, commentId: string): Promise<void> {
    return apiClient.delete(`/matches/${matchId}/comments/${commentId}/`);
  },

  async getMatchSheet(matchId: string): Promise<Blob> {
    return apiClient.getBlob(`/matches/${matchId}/match-sheet/`);
  },

  async getMatchTeamSheet(matchId: string, participantId: string): Promise<Blob> {
    return apiClient.getBlob(`/matches/${matchId}/team-sheet/${participantId}/`);
  },
};
