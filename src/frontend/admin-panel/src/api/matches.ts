import { apiClient } from './client';

// Response types
export interface MatchParticipantLineup {
    id: string;
    name: string;
    team_id: string;
    lineup: {
        player_id: string;
        player_name: string;
        player_course: string;
        is_starter: boolean;
        jersey_number?: number;
    }[];
    staff?: {
        id: string;
        staff_id: string;
        name: string;
    }[];
}

export interface MatchListItem {
  id: string;
  tournament: {
    id: string;
    name: string;
  };
  modality: string;
  location?: string;
  start_time: string;
  status: string;
  journey?: number;
  participants: {
    id: string;
    name: string;
    score?: number;
    position?: number;
    logo_url?: string;
  }[];
};

export interface MatchDetail extends MatchListItem {
  comments: {
    id: string;
    message: string;
    author_name: string;
    can_edit: boolean;
  }[];
}

export interface MatchPaginatedResponse {
  matches: MatchListItem[];
  total: number;
}

// Request types
export interface MatchListFilter {
  tournament_id?: string;
  status?: string;
  modality_id?: string;
  course_id?: string;
  date_from?: string; // ISO date string
  date_to?: string;   // ISO date string

  page?: number;
  limit?: number;
}

export interface MatchCreate {
  tournament_id: string;
  location?: string;
  start_time?: string;
  participants: string[];
  journey?: number;
  new_journey?: boolean;
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
  players: string[];
}

export interface LineupUpdate {
  players: {
    player_id: string;
    is_starter: boolean;
    jersey_number?: number | null;
  }[];
}

export const matchesApi = {
  // Match management
  async getAll(params?: MatchListFilter): Promise<MatchPaginatedResponse> {
    return apiClient.get<MatchPaginatedResponse>('/matches/', params );
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


  // Lineup management
  async getLineup(matchId: string, participantId: string): Promise<MatchParticipantLineup> {
    return apiClient.get<MatchParticipantLineup>(`/matches/${matchId}/lineups/${participantId}/`);
  },

  async assignLineup(matchId: string, participantId: string, data: LineupAssign): Promise<MatchParticipantLineup> {
    return apiClient.post<MatchParticipantLineup>(`/matches/${matchId}/lineups/${participantId}/`, data);
  },

  async updateLineup(matchId: string, participantId: string, data: LineupUpdate): Promise<MatchParticipantLineup> {
    return apiClient.put<MatchParticipantLineup>(`/matches/${matchId}/lineups/${participantId}/`, data);
  },

  async assignStaff(matchId: string, participantId: string, staffIds: string[]): Promise<MatchParticipantLineup> {
    return apiClient.post<MatchParticipantLineup>(`/matches/${matchId}/participants/${participantId}/staff/`, { staff_ids: staffIds });
  },

  // Comments management
  async addComment(matchId: string, data: CommentCreate): Promise<MatchDetail> {
    return apiClient.post<MatchDetail>(`/matches/${matchId}/comments/`, data);
  },

  async deleteComment(matchId: string, commentId: string): Promise<void> {
    return apiClient.delete(`/matches/${matchId}/comments/${commentId}/`);
  },

  // Match sheets
  async getMatchSheet(matchId: string): Promise<Blob> {
    return apiClient.getBlob(`/matches/${matchId}/match-sheet/`);
  },

  async getMatchTeamSheet(matchId: string, participantId: string): Promise<Blob> {
    return apiClient.getBlob(`/matches/${matchId}/team-sheet/${participantId}/`);
  },

};
