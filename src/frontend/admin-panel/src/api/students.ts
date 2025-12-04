import { apiClient } from './client';

export interface Student {
  id: number;
  course_id: number;
  full_name: string;
  student_number: string;
  email: string;
  is_member: boolean;
  member_type: 'student' | 'technical_staff';
}

export interface StudentCreate {
  full_name: string;
  student_number: string;
  email?: string;
  is_member: boolean;
  member_type?: 'student' | 'technical_staff';
}

export interface StudentUpdate {
  full_name?: string;
  email?: string;
  is_member?: boolean;
}

export const studentsApi = {
  async getAll(): Promise<Student[]> {
    return apiClient.get<Student[]>('/students');
  },

  async create(data: StudentCreate): Promise<Student> {
    return apiClient.post<Student>('/students', data);
  },

  async update(studentId: number, data: StudentUpdate): Promise<Student> {
    return apiClient.put<Student>(`/students/${studentId}`, data);
  },

  async delete(studentId: number): Promise<void> {
    return apiClient.delete(`/students/${studentId}`);
  },
};
