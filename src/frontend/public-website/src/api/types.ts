// API Response Types

export interface Course {
  id: string;
  name: string;
  abbreviation: string;
}

export interface Season {
  id: string;
  year: number;
  display_name: string;
  is_active: boolean;
}

export interface Modality {
  id: string;
  name: string;
  type: string;
  description?: string;
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
  id: string;
  name: string;
  modality: {
    id: string;
    name: string;
  };
  season: {
    id: string;
    year: number;
    display_name: string;
  };
  status: string;
  rules?: string;
  start_date?: string;
  team_count: number;
  rankings?: TournamentRankingEntry[];
}

export interface ModalityRanking {
  modality: {
    id: string;
    name: string;
  };
  season: {
    id: string;
    year: number;
    display_name: string;
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
    id: string;
    year: number;
    display_name: string;
  };
  course: {
    id: string;
    name: string;
    abbreviation: string;
  };
  total_points: number;
}
