import { apiClient } from './client';

export interface CourseListItem {
  id: string;
  name: string;
  abbreviation: string;
  nucleo: {
    id: string;
    name: string;
    abbreviation: string;
  };
  belongs_to_season: boolean;
  logo_url: string | null;
}

export interface CourseDetail extends CourseListItem {
  relevant_season_ids: number[]; // Seasons where this course is relevant (e.g., has active modalities)
};

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
  async getAll(seasonId?: number): Promise<CourseListItem[]> {
    return apiClient.get<CourseListItem[]>('/courses/', { season_id: seasonId });
  },

  async create(data: CourseCreate): Promise<CourseListItem> {
    return apiClient.post<CourseListItem>('/courses/', data);
  },

  async getById(courseId: string, seasonId?: number): Promise<CourseDetail> {
    return apiClient.get<CourseDetail>(`/courses/${courseId}/`, { season_id: seasonId });
  },

  async update(courseId: string, data: CourseUpdate): Promise<CourseDetail> {
    return apiClient.put<CourseDetail>(`/courses/${courseId}/`, data);
  },

  async addToSeason(courseId: string, seasonId: number): Promise<CourseDetail> {
    return apiClient.post<CourseDetail>(`/courses/${courseId}/add_to_season/`, { season_id: seasonId });
  },

  async removeFromSeason(courseId: string, seasonId: number): Promise<CourseDetail> {
    return apiClient.post<CourseDetail>(`/courses/${courseId}/remove_from_season/`, { season_id: seasonId });
  },

  async delete(courseId: string): Promise<void> {
    return apiClient.delete(`/courses/${courseId}/`);
  },
};
