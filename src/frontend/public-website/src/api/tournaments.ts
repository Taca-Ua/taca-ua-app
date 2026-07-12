import { apiCall, buildQueryString } from './client';

export interface TournamentDetail {
  tournament_id: string;
  tournament_name: string;
  start_date: string;
  status: string;
  modality_id: string;
  modality_name: string | null;
  modality_point_unit: string | null;
  modality_type_id: string;
  modality_type_name: string;
  competitor_count: number;
  match_count: number;
}

export interface TournamentDetailList {
  items: TournamentDetail[];
  total: number;
  page: number;
  page_size: number;
}

export interface TournamentListParams {
  page?: number;
  page_size?: number;
  modality_id?: string;
  status?: string;
  season_id?: number;
}

export interface TournamentStanding {
  id: number;
  tournament_id: string;
  competitor_type: string;
  competitor_entity_id: string;
  competitor_name: string;
  position: number;
  statistics_metadata: Record<string, any> | null;
}

export interface TournamentStandingsList {
  items: TournamentStanding[];
  total: number;
  page: number;
  page_size: number;
}

export interface StandingsParams {
  page?: number;
  page_size?: number;
}

export const tournamentsApi = {
  async getAll(params?: TournamentListParams): Promise<TournamentDetailList> {
    const queryParams: Record<string, string | undefined> = {
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
      modality_id: params?.modality_id,
      status: params?.status,
      season_id: params?.season_id?.toString(),
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<TournamentDetailList>(`/tournaments${queryString}`);
  },

  async getById(tournamentId: string): Promise<TournamentDetail> {
    return apiCall<TournamentDetail>(`/tournaments/${tournamentId}`);
  },

  async getStandings(
    tournamentId: string,
    params?: StandingsParams
  ): Promise<TournamentStandingsList> {
    const queryParams: Record<string, string | undefined> = {
      page: params?.page?.toString(),
      page_size: params?.page_size?.toString(),
    };
    const queryString = buildQueryString(queryParams);
    return apiCall<TournamentStandingsList>(
      `/tournaments/${tournamentId}/standings${queryString}`
    );
  },
};
