import { apiCall, buildQueryString } from './client';

export interface NucleoPublic {
  nucleo_id: string;
  name: string;
  abbreviation: string;
  logo_url?: string;
}

export interface NucleoList {
  items: NucleoPublic[];
  total: number;
  page: number;
  page_size: number;
}

export const nucleosApi = {
  async getAll(params?: { page?: number; page_size?: number }): Promise<NucleoList> {
    const queryString = buildQueryString({
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
    });
    return apiCall<NucleoList>(`/nucleos${queryString}`);
  },

  async getById(nucleoId: string): Promise<NucleoPublic> {
    return apiCall<NucleoPublic>(`/nucleos/${nucleoId}`);
  },
};
