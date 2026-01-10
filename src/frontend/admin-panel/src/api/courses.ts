import { apiClient } from './client';


export interface Course {
  id: string;
  name: string;
  abbreviation: string;
}

export interface CourseDetail extends Course {
  nucleo: string;
}

export interface CourseCreate {
  abbreviation: string;
  name: string;
  description?: string;
  logo_url?: string;
  nucleo_id: string;
}

export interface CourseUpdate {
  abbreviation?: string;
  name?: string;
  description?: string;
  logo_url?: string;
  nucleo_id?: string;
}

export const coursesApi = {
  async getAll(): Promise<Course[]> {
    return apiClient.get<Course[]>('/courses');
  },

  async getById(courseId: string): Promise<CourseDetail> {
    return apiClient.get<CourseDetail>(`/courses/${courseId}`);
  },

  async create(data: CourseCreate): Promise<CourseDetail> {
    return apiClient.post<CourseDetail>('/courses', data);
  },

  async update(courseId: string, data: CourseUpdate): Promise<CourseDetail> {
    return apiClient.put<CourseDetail>(`/courses/${courseId}`, data);
  },

  async delete(courseId: string): Promise<void> {
    return apiClient.delete(`/courses/${courseId}`);
  },
};
