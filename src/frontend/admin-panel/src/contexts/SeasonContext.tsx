import React, { createContext, useContext, useEffect, useState } from "react";
import { seasonsApi, type SeasonListItem } from "../api/seasons";
import { useAuth } from "../hooks/useAuth";

type SeasonContextType = {
  loadedSeason: SeasonListItem | null;
  activeSeason: SeasonListItem | null;
  selectSeason: (season: SeasonListItem) => void;
  availableSeasons: SeasonListItem[];
};

const SeasonContext = createContext<SeasonContextType | null>(null);

export const useSeason = () => useContext(SeasonContext)!;

export const SeasonProvider = ({ children }: { children: React.ReactNode }) => {
  const [seasons, setSeasons] = useState<SeasonListItem[]>([]);
  const [activeSeason, setActiveSeason] = useState<SeasonListItem | null>(null);
  const [loadedSeason, setLoadedSeason] = useState<SeasonListItem | null>(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) return; // Don't fetch seasons if not authenticated
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
    fetchSeasons();
  }, [isAuthenticated]); // Refetch seasons when authentication status changes

  return (
    <SeasonContext.Provider value={{ loadedSeason, activeSeason, availableSeasons: seasons, selectSeason: setLoadedSeason }}>
      {children}
    </SeasonContext.Provider>
  );
};
