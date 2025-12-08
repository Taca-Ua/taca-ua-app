// API Response Types

export interface Course {
  id: string;
  name: string;
  abbreviation: string;
}

export interface Season {
  id: number;
  year: number;
  status: 'draft' | 'active' | 'finished';
}

export interface Modality {
  id: number;
  name: string;
  type: string;
  scoring_schema?: Record<string, number>;
}

export interface Team {
  id: string;
  name: string;
  course: {
    id: string;
    name: string;
    abbreviation: string;
  };
  modality: {
    id: string;
    name: string;
  };
  player_count: number;
}

export interface Match {
  id: string;
  tournament_id: string;
  tournament_name: string;
  team_home: {
    id: string;
    name: string;
    course_abbreviation: string;
  };
  team_away: {
    id: string;
    name: string;
    course_abbreviation: string;
  };
  modality: {
    id: string;
    name: string;
  };
  start_time: string;
  location: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score?: number;
  away_score?: number;
}

export interface TournamentRankingEntry {
  position: number;
  team_id: number;
  team_name: string;
  course_id: number;
  course_name: string;
  course_short_code: string;
  points: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
}

export interface TournamentPublicDetail {
  id: number;
  name: string;
  modality: {
    id: number;
    name: string;
  };
  season: {
    id: number;
    year: number;
  };
  status: string;
  rules?: string;
  start_date?: string;
  team_count: number;
  rankings?: TournamentRankingEntry[];
}

export interface ModalityRanking {
  modality: {
    id: number;
    name: string;
  };
  season: {
    id: number;
    year: number;
  };
  rankings: TournamentRankingEntry[];
}

export interface GeneralRanking {
  position: number;
  course: {
    id: string;
    name: string;
    abbreviation: string;
  };
  total_points: number;
  breakdown: {
    [modalityName: string]: number;
  };
}

// RankingEntry shape (backend public API - general rankings)
export interface RankingEntry {
  position: number;
  course_id: number | string;
  course_name: string;
  course_short_code: string;
  points: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
}

// Response wrapper returned by /rankings/general
export interface GeneralRankingResponse {
  season_id: number;
  season_year: number;
  rankings: RankingEntry[];
}

export interface Regulation {
  id: string;
  title: string;
  description?: string;
  file_url: string;
  category?: string;
  created_at: string;
  updated_at: string;
}

export interface HistoricalWinner {
  season: {
    id: number;
    year: number;
  };
  course: {
    id: string;
    name: string;
    abbreviation: string;
  };
  total_points: number;
}
