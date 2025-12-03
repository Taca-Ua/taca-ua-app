import { apiCall } from './client';
import type { Course } from './types';

export const coursesApi = {
  /**
   * Get all courses
   */
  getCourses: async (): Promise<Course[]> => {
    return apiCall<Course[]>('/courses');
  },

  /**
   * Get a specific course by ID
   */
  getCourse: async (courseId: string): Promise<Course> => {
    return apiCall<Course>(`/courses/${courseId}`);
  },
};
