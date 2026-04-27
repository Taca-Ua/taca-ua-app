import { apiCall, buildQueryString } from './client';

export interface Regulation {
  id: string;
  title: string;
  description?: string;
  file_url: string;
}

export async function getRegulations(search?: string): Promise<Regulation[]> {
  const qs = buildQueryString({ search });
  return apiCall<Regulation[]>(`/regulations${qs}`);
}
