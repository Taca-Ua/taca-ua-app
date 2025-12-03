import { apiCall, buildQueryString } from './client';
import type { TournamentPublicDetail, TournamentRankingEntry } from './types';

export interface GetTournamentsParams {
  modality_id?: string;
  season_id?: string;
  status?: string;
}

export const tournamentsApi = {
  /**
   * Get all tournaments with optional filters
   */
  getTournaments: async (params?: GetTournamentsParams): Promise<TournamentPublicDetail[]> => {
    const query = params ? buildQueryString(params as Record<string, string | undefined>) : '';
    return apiCall<TournamentPublicDetail[]>(`/tournaments${query}`);
  },

  /**
   * Get tournament details by ID
   */
  getTournamentDetail: async (tournamentId: string, includeRankings = false): Promise<TournamentPublicDetail> => {
    const query = includeRankings ? '?include_rankings=true' : '';
    return apiCall<TournamentPublicDetail>(`/tournaments/${tournamentId}${query}`);
  },

  /**
   * Get tournament rankings
   */
  getTournamentRankings: async (tournamentId: string): Promise<TournamentRankingEntry[]> => {
    return apiCall<TournamentRankingEntry[]>(`/tournaments/${tournamentId}/rankings`);
  },
};
