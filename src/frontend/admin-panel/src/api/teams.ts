import { apiClient } from './client';

export interface Player {
  id: string;
  full_name: string;
  student_number: string;
}

export interface Team {
  id: string;
  modality_name: string;
  course_name: string;
  course_id: string;
  name: string;
  players: Player[];
}

export interface TeamCreate {
  name: string;
  modality_id: string;
  course_id: string;
}

export interface TeamUpdate {
  name?: string;
  modality_id?: string;
  course_id?: string;
  players_add?: string[];  // IDs of players to add
  players_remove?: string[];  // IDs of players to remove
}

export const teamsApi = {
  async getAll(modality_id?: string): Promise<Team[]> {
    const params = modality_id ? { modality_id } : undefined;
    return apiClient.get<Team[]>('/teams/', params);
  },

  async get(teamId: string): Promise<Team> {
	return apiClient.get<Team>(`/teams/${teamId}/`);
  },

  async create(data: TeamCreate): Promise<Team> {
    return apiClient.post<Team>('/teams/', data);
  },

  async update(teamId: string, data: TeamUpdate): Promise<Team> {
    return apiClient.put<Team>(`/teams/${teamId}/`, data);
  },

  async delete(teamId: string): Promise<void> {
    return apiClient.delete(`/teams/${teamId}/`);
  },
};
