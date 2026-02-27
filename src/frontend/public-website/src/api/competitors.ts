import { apiCall } from './client';
import { type TournamentStanding } from './tournaments';

export const competitorsApi = {
  async getStandings(competitorId: string): Promise<TournamentStanding[]> {
    return apiCall<TournamentStanding[]>(`/competitors/${competitorId}/standings`);
  },
};
