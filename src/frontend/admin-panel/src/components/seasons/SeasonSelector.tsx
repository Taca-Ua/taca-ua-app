import { useState } from "react";
import { useSeason } from "../../contexts/SeasonContext";

const SeasonSelector = ({
    relevantSeasonIds,
}: {
    relevantSeasonIds?: number[];
}) => {

  // Upper bar component to select the season, shows the currently loaded season and allows changing it like a tab selector
  const { availableSeasons, loadedSeason, selectSeason } = useSeason();
  const [isChangingSeason, setIsChangingSeason] = useState(false);

  const handleSeasonChange = async (seasonId: number) => {
    try {
      setIsChangingSeason(true);
      const selectedSeason = availableSeasons.find(s => s.id === seasonId);
      if (!selectedSeason) throw new Error("Selected season not found");
      await selectSeason(selectedSeason);
    } catch (error) {
      console.error("Failed to change season:", error);
    } finally {
      setIsChangingSeason(false);
    }
  };


  const isRelevant = (seasonId: number) => relevantSeasonIds?.includes(seasonId) ?? false;
  const isActive = (seasonId: number) => seasonId === loadedSeason?.id;

  return (
    <div className="flex flex-col space-y-2">
      {/* Season selector buttons */}
      <div className="flex items-center space-x-4">
        {availableSeasons.map(season => {
          const active = isActive(season.id);
          const relevant = isRelevant(season.id);

          let buttonClass = "px-3 py-1 rounded transition-colors duration-200";

          if (active) {
            // Active state: loaded season
            buttonClass += " bg-teal-600 text-white font-semibold";
          } else if (relevant) {
            // Relevant state: season is relevant but not loaded (e.g., modality active in this season)
            buttonClass += " bg-teal-200 text-teal-900 hover:bg-teal-300 border border-teal-400";
          } else {
            // Inactive state: not relevant or not loaded
            buttonClass += " bg-gray-200 text-gray-700 hover:bg-gray-300";
          }

          return (
            <button
              key={season.id}
              onClick={() => handleSeasonChange(season.id)}
              disabled={isChangingSeason || active}
              className={buttonClass}
              title={
                relevant && !active
                  ? `This entity is active in ${season.name}`
                  : undefined
              }
            >
              {season.name}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default SeasonSelector;
