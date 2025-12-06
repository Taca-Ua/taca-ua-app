import { apiCall, buildQueryString } from './client';
import type { TournamentPublicDetail, TournamentRankingEntry } from './types';

export interface GetTournamentsParams {
  modality_id?: number | string;
  season_id?: number | string;
  status?: string;
}

export const tournamentsApi = {
  /**
   * Get all tournaments with optional filters
   */
  getTournaments: async (params?: GetTournamentsParams): Promise<TournamentPublicDetail[]> => {
    const query = params ? buildQueryString({
      modality_id: params.modality_id ? String(params.modality_id) : undefined,
      season_id: params.season_id ? String(params.season_id) : undefined,
      status: params.status,
    }) : '';
    return apiCall<TournamentPublicDetail[]>(`/tournaments${query}`);
  },

  /**
   * Get tournament details by ID
   */
  getTournamentDetail: async (tournamentId: number | string, includeRankings = false): Promise<TournamentPublicDetail> => {
    const query = includeRankings ? '?include_rankings=true' : '';
    return apiCall<TournamentPublicDetail>(`/tournaments/${tournamentId}${query}`);
  },

  /**
   * Get tournament rankings
   */
  getTournamentRankings: async (tournamentId: number | string): Promise<TournamentRankingEntry[]> => {
    return apiCall<TournamentRankingEntry[]>(`/tournaments/${tournamentId}/rankings`);
  },
};
