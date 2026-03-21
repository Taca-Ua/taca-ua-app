import { apiClient } from './client';
import type { Course } from './courses';

// Student interface
export interface Student {
  id: string;
  full_name: string;
  course: Course;
  student_number: string;
  is_member: boolean;
}

export interface StudentDetail extends Student {
  // Additional fields can be added here if needed
}

export interface StudentCreate {
  full_name: string;
  course_id: string;
  student_number: string;
  is_member: boolean;
}

export interface StudentUpdate {
  full_name?: string;
  course_id?: string;
  student_number?: string;
  is_member?: boolean;
}

export interface StudentListParams {
  course_id?: string;
}

// Staff interface
export interface Staff {
  id: string;
  full_name: string;
  staff_number?: string;
  contact?: string;
}

export interface StaffDetail extends Staff {
  // Additional fields can be added here if needed
}

export interface StaffCreate {
  full_name: string;
  staff_number?: string;
  contact?: string;
}

export interface StaffUpdate {
  full_name?: string;
  staff_number?: string;
  contact?: string;
}

// Students API
export const studentsApi = {
  async getAll(params?: StudentListParams): Promise<Student[]> {
    return apiClient.get<Student[]>(`/students/`, params);
  },

  async create(data: StudentCreate): Promise<Student> {
    return apiClient.post<Student>('/students/', data);
  },

  async getById(id: string): Promise<StudentDetail> {
    return apiClient.get<StudentDetail>(`/students/${id}/`);
  },

  async update(id: string, data: StudentUpdate): Promise<StudentDetail> {
    return apiClient.put<StudentDetail>(`/students/${id}/`, data);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/students/${id}/`);
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

// Staff API
export const staffApi = {
  async getAll(): Promise<Staff[]> {
    return apiClient.get<Staff[]>('/staff/');
  },

  async create(data: StaffCreate): Promise<Staff> {
    return apiClient.post<Staff>('/staff/', data);
  },

  async getById(id: string): Promise<StaffDetail> {
    return apiClient.get<StaffDetail>(`/staff/${id}/`);
  },

  async update(id: string, data: StaffUpdate): Promise<StaffDetail> {
    return apiClient.put<StaffDetail>(`/staff/${id}/`, data);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/staff/${id}/`);
  },
};
