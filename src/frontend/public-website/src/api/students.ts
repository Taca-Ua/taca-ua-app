import { apiCall, buildQueryString } from './client';

export interface StudentDetail {
  student_id: string;
  student_number: string;
  full_name: string;
  is_member: boolean;
  course_id: string;
  course_name: string;
  course_abbreviation: string;
  nucleo_id: string;
  nucleo_name: string;
  nucleo_abbreviation: string;
  team_count: number;
  updated_at: string;
}

export interface StudentDetailList {
  items: StudentDetail[];
  total: number;
  page: number;
  page_size: number;
}

export interface StudentListParams {
  page?: number;
  page_size?: number;
  course_id?: string;
  nucleo_id?: string;
  is_member?: boolean;
  search?: string;
}

export const studentsApi = {
  async getAll(params?: StudentListParams): Promise<StudentDetailList> {
    const queryParams: Record<string, string | undefined> = {
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
      course_id: params?.course_id,
      nucleo_id: params?.nucleo_id,
      is_member: params?.is_member?.toString(),
      search: params?.search,
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<StudentDetailList>(`/students${queryString}`);
  },

  async getById(studentId: string): Promise<StudentDetail> {
    return apiCall<StudentDetail>(`/students/${studentId}`);
  },

  async getByNumber(studentNumber: string): Promise<StudentDetail> {
    return apiCall<StudentDetail>(`/students/by-number/${studentNumber}`);
  },
};
