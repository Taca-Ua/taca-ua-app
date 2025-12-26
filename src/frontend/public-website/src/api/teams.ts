import { apiCall, buildQueryString } from './client';
import type { Team } from './types';

export interface GetTeamsParams {
  course_id?: string;
  modality_id?: string;
}

export const teamsApi = {
  /**
   * Get all teams with optional filters
   */
  getTeams: async (params?: GetTeamsParams): Promise<Team[]> => {
    const query = params ? buildQueryString(params as Record<string, string | undefined>) : '';
    return apiCall<Team[]>(`/teams${query}`);
  },

  /**
   * Get a specific team by ID
   */
  getTeam: async (teamId: string): Promise<Team> => {
    return apiCall<Team>(`/teams/${teamId}`);
  },
};
