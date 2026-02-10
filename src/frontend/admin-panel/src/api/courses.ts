import { apiClient } from './client';
import { type Nucleo } from './nucleos';

export interface Course {
  id: string;
  name: string;
  abbreviation: string;
  nucleo: Nucleo;
}

export interface CourseDetail extends Course {
  created_at: string;
}

export interface CourseCreate {
  name: string;
  abbreviation: string;
  nucleo_id: string;
}

export interface CourseUpdate {
  name?: string;
  abbreviation?: string;
  nucleo_id?: string;
}

export const coursesApi = {
  async getAll(): Promise<Course[]> {
    return apiClient.get<Course[]>('/courses/');
  },

  async getById(courseId: string): Promise<CourseDetail> {
    return apiClient.get<CourseDetail>(`/courses/${courseId}/`);
  },

  async create(data: CourseCreate): Promise<Course> {
    return apiClient.post<Course>('/courses/', data);
  },

  async update(courseId: string, data: CourseUpdate): Promise<CourseDetail> {
    return apiClient.put<CourseDetail>(`/courses/${courseId}/`, data);
  },

  async delete(courseId: string): Promise<void> {
    return apiClient.delete(`/courses/${courseId}/`);
  },
};
