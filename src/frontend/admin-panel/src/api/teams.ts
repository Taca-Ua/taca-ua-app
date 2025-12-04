import { apiClient } from './client';

export interface Team {
  id: number;
  modality_id: number;
  course_id: number;
  name: string;
  players: number[];
}

export interface TeamCreate {
  modality_id: number;
  name: string;
  players?: number[];
}

export interface TeamUpdate {
  name?: string;
  players_add?: number[];
  players_remove?: number[];
}

export const teamsApi = {
  async getAll(includeAll = false): Promise<Team[]> {
    const params = includeAll ? { all: 'true' } : undefined;
    return apiClient.get<Team[]>('/teams', params);
  },

  async create(data: TeamCreate): Promise<Team> {
    return apiClient.post<Team>('/teams', data);
  },

  async update(teamId: number, data: TeamUpdate): Promise<Team> {
    return apiClient.put<Team>(`/teams/${teamId}`, data);
  },

  async delete(teamId: number): Promise<void> {
    return apiClient.delete(`/teams/${teamId}`);
  },
};
