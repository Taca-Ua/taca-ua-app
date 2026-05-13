import { apiCall, buildQueryString } from './client';

export interface Regulation {
  id: string;
  title: string;
  description?: string;
  file_url: string;
}

export async function getRegulations(search?: string, season_id?: number): Promise<Regulation[]> {
  const qs = buildQueryString({ search, season_id: season_id?.toString() });
  return apiCall<Regulation[]>(`/regulations${qs}`);
}
