import { apiClient } from './client';

export interface Course {
  id: string;
  abbreviation: string;
  name: string;
  description?: string;
  logo_url?: string;
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

  async getById(courseId: string): Promise<Course> {
    return apiClient.get<Course>(`/courses/${courseId}`);
  },

  async create(data: CourseCreate): Promise<Course> {
    return apiClient.post<Course>('/courses', data);
  },

  async update(courseId: string, data: CourseUpdate): Promise<Course> {
    return apiClient.put<Course>(`/courses/${courseId}`, data);
  },

  async delete(courseId: string): Promise<void> {
    return apiClient.delete(`/courses/${courseId}`);
  },
};
