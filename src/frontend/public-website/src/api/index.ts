// Export all API modules
export * from './types';
export * from './courses';
export * from './seasons';
export * from './modalities';
export * from './teams';
export * from './matches';
export * from './tournaments';
export * from './rankings';
export * from './regulations';
export * from './history';

// Main API object for convenience
import { coursesApi } from './courses';
import { seasonsApi } from './seasons';
import { modalitiesApi } from './modalities';
import { teamsApi } from './teams';
import { matchesApi } from './matches';
import { tournamentsApi } from './tournaments';
import { rankingsApi } from './rankings';
import { regulationsApi } from './regulations';
import { historyApi } from './history';

export const api = {
  courses: coursesApi,
  seasons: seasonsApi,
  modalities: modalitiesApi,
  teams: teamsApi,
  matches: matchesApi,
  tournaments: tournamentsApi,
  rankings: rankingsApi,
  regulations: regulationsApi,
  history: historyApi,
};

export default api;
