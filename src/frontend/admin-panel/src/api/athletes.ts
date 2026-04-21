import { apiClient } from './client2';

export interface AthleteListItem {
    id: string;
    full_name: string;

    course: {
        name: string;
        abbreviation: string;
    },

    student_number: string;
    is_member: boolean;
};

export interface AthleteDetail extends AthleteListItem {};


export interface AthleteListParams {
    course_id?: string;
};

export interface AthleteCreate {
    full_name: string;
    course_id: string;
    student_number: string;
    is_member?: boolean;
}

export interface AthleteUpdate {
    full_name?: string;
    course_id?: string;
    student_number?: string;
    is_member?: boolean;
};

export interface AthleteMembershipSync {
    student_numbers?: string[];
}

export const athletesApi = {
  async getAll(params?: AthleteListParams): Promise<AthleteListItem[]> {
    return apiClient.get<AthleteListItem[]>('/athletes/', { params });
  },

  async create(data: AthleteCreate): Promise<AthleteListItem> {
    return apiClient.post<AthleteListItem>('/athletes/', data);
  },

  async syncMembership(data: AthleteMembershipSync): Promise<void> {
    return apiClient.post('/athletes/sync-membership/', data);
  },

  async getById(athleteId: string): Promise<AthleteDetail> {
    return apiClient.get<AthleteDetail>(`/athletes/${athleteId}/`);
  },

  async update(athleteId: string, data: AthleteUpdate): Promise<AthleteDetail> {
    return apiClient.put<AthleteDetail>(`/athletes/${athleteId}/`, data);
  },

  async delete(athleteId: string): Promise<void> {
    return apiClient.delete(`/athletes/${athleteId}/`);
  },

  async syncMembershipFromNmecList(studentNumbers: string[]): Promise<{
      participants_in_scope: number;
      reset_to_non_socio: number;
      set_as_socio: number;
      unmatched_numbers: string[];
    }> {
      return apiClient.post('/students/sync-membership/', {
        student_numbers: studentNumbers,
      });
    },
};
