import { apiClient } from './client';
import { type Modality } from "./modalities";
import { type Course } from './courses';
import { type Student } from "./members";

export interface Team {
  id: string;
  name: string;
  modality: Modality;
  course: Course;
}

export interface TeamDetail extends Team {
  players: Student[];
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

// Params interfaces
export interface TeamListParams {
  modality_id?: string;
  course_id?: string;
}

export const teamsApi = {
  async getAll(params?: TeamListParams): Promise<Team[]> {
    return apiClient.get<Team[]>('/teams/', params);
  },

  async create(data: TeamCreate): Promise<Team> {
    return apiClient.post<Team>('/teams/', data);
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
