import { apiClient } from './client';

export interface TeamListItem {
  id: string;
  name: string;
  modality: {
    id: string;
    name: string;
  };
  course: {
    id: string;
    name: string;
    abbreviation: string;
  };
}

export interface TeamDetail extends TeamListItem {
  players: {
    id: string;
    full_name: string;
    student_number: string;
  }[];
  season: {
    id: number;
    name: string;
  }
}

export interface TeamCreate {
  name: string;
  modality_id: string;
  course_id: string;
  season_id?: number;
}

export interface TeamUpdate {
  name?: string;
  players_add?: string[];  // IDs of players to add
  players_remove?: string[];  // IDs of players to remove
}

// Params interfaces
export interface TeamListParams {
  season_id?: number;
  modality_id?: string;
  course_id?: string;
}

export const teamsApi = {
  async getAll(params?: TeamListParams): Promise<TeamListItem[]> {
    return apiClient.get<TeamListItem[]>('/teams/', params);
  },

  async create(data: TeamCreate): Promise<TeamListItem> {
    return apiClient.post<TeamListItem>('/teams/', data);
  },

  async get(teamId: string): Promise<TeamDetail> {
	return apiClient.get<TeamDetail>(`/teams/${teamId}/`);
  },

  async update(teamId: string, data: TeamUpdate): Promise<TeamDetail> {
    return apiClient.put<TeamDetail>(`/teams/${teamId}/`, data);
  },

  async delete(teamId: string): Promise<void> {
    return apiClient.delete(`/teams/${teamId}/`);
  },
};
