import { apiCall, buildQueryString } from './client';

export interface CoursePublicSimple {
  course_id: string;
  name: string;
  abbreviation: string;
}

export interface CoursePublic extends CoursePublicSimple {
    nucleo_id: string;
    nucleo_name: string;
    nucleo_abbreviation: string;
    nucleo_logo_url: string;
}

export interface CourseList {
  items: CoursePublic[];
  total: number;
  page: number;
  page_size: number;
}

export interface CourseListSimple {
  items: CoursePublicSimple[];
  total: number;
}

export interface CourseListParams {
  page?: number;
  page_size?: number;
}


export const coursesApi = {
  async getAll(params?: CourseListParams): Promise<CourseList> {
    const queryString = buildQueryString({
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
    });
    return apiCall<CourseList>(`/courses${queryString}`);
  },

  async getAllSimple(): Promise<CourseListSimple> {
    return apiCall<CourseListSimple>(`/courses/menu`);
  }
};
