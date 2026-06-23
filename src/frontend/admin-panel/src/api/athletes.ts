import { apiClient } from './client';

export interface AthleteListItem {
    id: string;
    name: string;

    course: {
        id: string;
        name: string;
        abbreviation: string;
    },

    student_number: string;
    is_member: boolean;
};

export interface AthleteDetail extends AthleteListItem {
    course_proof_file_url?: string;
    payment_proof_file_url?: string;
};


export interface AthleteListParams {
    course_id?: string;
    team_id?: string;
};

export interface AthleteCreate {
    name: string;
    course_id: string;
    student_number: string;
    is_member?: boolean;
    course_proof?: File;
    payment_proof?: File;
}

export interface AthleteUpdate {
    name?: string;
    course_id?: string;
    student_number?: string;
    is_member?: boolean;
    course_proof?: File | null;
    payment_proof?: File | null;
};

export interface AthleteMembershipSync {
    student_numbers?: string[];
}

export const athletesApi = {
  async getAll(params?: AthleteListParams): Promise<AthleteListItem[]> {
    return apiClient.get<AthleteListItem[]>('/athletes/', params );
  },

  async create(data: AthleteCreate): Promise<AthleteListItem> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('course_id', data.course_id);
    formData.append('student_number', data.student_number);
    if (data.is_member !== undefined) {
      formData.append('is_member', String(data.is_member));
    }
    if (data.course_proof) {
      formData.append('course_proof', data.course_proof);
    }
    if (data.payment_proof) {
      formData.append('payment_proof', data.payment_proof);
    }
    return apiClient.post<AthleteListItem>('/athletes/', formData);
  },

  async syncMembership(data: AthleteMembershipSync): Promise<void> {
    return apiClient.post('/athletes/sync-membership/', data);
  },

  async getById(athleteId: string): Promise<AthleteDetail> {
    return apiClient.get<AthleteDetail>(`/athletes/${athleteId}/`);
  },

  async update(athleteId: string, data: AthleteUpdate): Promise<AthleteDetail> {
    const formData = new FormData();
    if (data.name !== undefined) {
      formData.append('name', data.name);
    }
    if (data.course_id !== undefined) {
      formData.append('course_id', data.course_id);
    }
    if (data.student_number !== undefined) {
      formData.append('student_number', data.student_number);
    }
    if (data.is_member !== undefined) {
      formData.append('is_member', String(data.is_member));
    }
    if (data.course_proof !== undefined) {
      if (data.course_proof === null) {
        formData.append('course_proof_deleted', 'true');
      } else {
        formData.append('course_proof', data.course_proof);
      }
    }
    if (data.payment_proof !== undefined) {
      if (data.payment_proof === null) {
        formData.append('payment_proof_deleted', 'true');
      } else {
        formData.append('payment_proof', data.payment_proof);
      }
    }
    return apiClient.put<AthleteDetail>(`/athletes/${athleteId}/`, formData);
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
