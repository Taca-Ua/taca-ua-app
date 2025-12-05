import { apiClient } from './client';

export interface Course {
  id: number;
  abbreviation: string;
  name: string;
  description?: string;
}

export const coursesApi = {
  async getAll(): Promise<Course[]> {
    return apiClient.get<Course[]>('/courses');
  },

  async getById(courseId: number): Promise<Course> {
    return apiClient.get<Course>(`/courses/${courseId}`);
  },
};
