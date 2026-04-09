import { apiCall, buildQueryString } from './client';

export interface TeamDetail {
  team_id: string;
  team_name: string;
  course_id: string;
  course_name: string;
  course_abbreviation: string;
  nucleo_id: string;
  nucleo_name: string;
  nucleo_abbreviation: string;
  modality_id: string;
  modality_name: string | null;
  modality_type_id: string;
  modality_type_name: string;
  player_count: number;
  players?: {
    student_id: string;
    student_number: string;
    full_name: string;
    is_member: boolean;
  }[];
}

export interface TeamDetailList {
  items: TeamDetail[];
  total: number;
  page: number;
  page_size: number;
}

export interface TeamListParams {
  page?: number;
  page_size?: number;
  course_id?: string;
  nucleo_id?: string;
  modality_id?: string;
}

export const teamsApi = {
  async getAll(params?: TeamListParams): Promise<TeamDetailList> {
    const queryParams: Record<string, string | undefined> = {
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
      course_id: params?.course_id,
      nucleo_id: params?.nucleo_id,
      modality_id: params?.modality_id,
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<TeamDetailList>(`/teams${queryString}`);
  },

  async getById(teamId: string): Promise<TeamDetail> {
    return apiCall<TeamDetail>(`/teams/${teamId}`);
  },
};
