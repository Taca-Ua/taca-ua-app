import { apiClient } from './client';

export interface Course {
  id: number;
  abbreviation: string;
  name: string;
  description?: string;
  logo_url?: string;
}

export interface CourseCreate {
  abbreviation: string;
  name: string;
  description?: string;
  logo_url?: string;
}

export interface CourseUpdate {
  abbreviation?: string;
  name?: string;
  description?: string;
  logo_url?: string;
}

export const coursesApi = {
  async getAll(): Promise<Course[]> {
    return apiClient.get<Course[]>('/courses');
  },

  async getById(courseId: number): Promise<Course> {
    return apiClient.get<Course>(`/courses/${courseId}`);
  },

  async create(data: CourseCreate): Promise<Course> {
    return apiClient.post<Course>('/courses', data);
  },

  async update(courseId: number, data: CourseUpdate): Promise<Course> {
    return apiClient.put<Course>(`/courses/${courseId}`, data);
  },

  async delete(courseId: number): Promise<void> {
    return apiClient.delete(`/courses/${courseId}`);
  },
};
