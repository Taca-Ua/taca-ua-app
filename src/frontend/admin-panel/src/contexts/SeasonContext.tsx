import React, { createContext, useContext, useEffect, useState } from "react";
import { seasonsApi, type SeasonListItem } from "../api/seasons";
import { useAuth } from "../hooks/useAuth";

type SeasonContextType = {
  currentSeason: SeasonListItem | null;
  availableSeasons: SeasonListItem[];
  setCurrentSeason: (season: SeasonListItem) => void;
};

const SeasonContext = createContext<SeasonContextType | null>(null);

export const useSeason = () => useContext(SeasonContext)!;

export const SeasonProvider = ({ children }: { children: React.ReactNode }) => {
  const [seasons, setSeasons] = useState<SeasonListItem[]>([]);
  const [currentSeason, setCurrentSeason] = useState<SeasonListItem | null>(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) return; // Don't fetch seasons if not authenticated
    const fetchSeasons = async () => {
      try {
        const allSeasons = await seasonsApi.getAll();
        // const activeSeason = await seasonsApi.getCurrent();
        console.log("Fetched seasons:", allSeasons);
        setSeasons(allSeasons);
        setCurrentSeason(allSeasons[allSeasons.length - 1] || null); // Set the last season as current by default
        // setCurrentSeason(activeSeason);
      } catch (error) {
        console.error("Failed to fetch seasons:", error);
      }
    };
    fetchSeasons();
  }, [isAuthenticated]); // Refetch seasons when authentication status changes

  return (
    <SeasonContext.Provider value={{ currentSeason, availableSeasons: seasons, setCurrentSeason }}>
      {children}
    </SeasonContext.Provider>
  );
};
