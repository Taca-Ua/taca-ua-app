import { apiClient } from './client2';

export interface CourseListItem {
  id: string;
  name: string;
  abbreviation: string;
  nucleo: {
    id: string;
    name: string;
    abbreviation: string;
  };
}

export interface CourseDetail extends CourseListItem {};

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
  async getAll(): Promise<CourseListItem[]> {
    return apiClient.get<CourseListItem[]>('/courses/');
  },

  async create(data: CourseCreate): Promise<CourseListItem> {
    return apiClient.post<CourseListItem>('/courses/', data);
  },

  async getById(courseId: string): Promise<CourseDetail> {
    return apiClient.get<CourseDetail>(`/courses/${courseId}/`);
  },

  async update(courseId: string, data: CourseUpdate): Promise<CourseDetail> {
    return apiClient.put<CourseDetail>(`/courses/${courseId}/`, data);
  },

  async delete(courseId: string): Promise<void> {
    return apiClient.delete(`/courses/${courseId}/`);
  },
};
