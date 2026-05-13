import React, { createContext, useContext, useEffect, useState } from "react";
import { seasonsApi, type SeasonListItem } from "../api/seasons";
import { useAuth } from "../hooks/useAuth";

type SeasonContextType = {
  loadedSeason: SeasonListItem | null;
  activeSeason: SeasonListItem | null;
  selectSeason: (season: SeasonListItem) => void;
  availableSeasons: SeasonListItem[];
  loadedSeasonIsTheCurrentSeason: boolean;
  refreshSeasons: () => void;
};

const SeasonContext = createContext<SeasonContextType | null>(null);

export const useSeason = () => useContext(SeasonContext)!;

export const SeasonProvider = ({ children }: { children: React.ReactNode }) => {
  const [seasons, setSeasons] = useState<SeasonListItem[]>([]);
  const [activeSeason, setActiveSeason] = useState<SeasonListItem | null>(null);
  const [loadedSeason, setLoadedSeason] = useState<SeasonListItem | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchSeasons = async () => {
    try {
      const [allSeasons, activeSeason] = await Promise.all([
        seasonsApi.getAll(),
        seasonsApi.getCurrent(),
      ]);
      setSeasons(allSeasons);
      setLoadedSeason(activeSeason);
      setActiveSeason(activeSeason);
    } catch (error) {
      console.error("Failed to fetch seasons:", error);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) return; // Don't fetch seasons if not authenticated
    fetchSeasons();
  }, [isAuthenticated]); // Refetch seasons when authentication status changes

  return (
    <SeasonContext.Provider value={{
      loadedSeason,
      activeSeason,
      availableSeasons: seasons,
      selectSeason: setLoadedSeason,
      loadedSeasonIsTheCurrentSeason: loadedSeason?.id === activeSeason?.id,
      refreshSeasons: fetchSeasons
    }}>
      {children}
    </SeasonContext.Provider>
  );
};
