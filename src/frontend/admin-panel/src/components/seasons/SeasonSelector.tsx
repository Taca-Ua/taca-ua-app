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
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="border-b border-gray-200 overflow-auto">
        <div className="flex">
          {availableSeasons.map(season => {
            const active = isActive(season.id);
            const relevant = isRelevant(season.id);

            let buttonClass = "px-6 py-4 font-bold transition-colors border-b-2 flex-shrink-0";

            if (active) {
              // Active state: loaded season
              buttonClass += " border-teal-600 text-teal-600";
            } else if (relevant) {
              // Relevant state: season is relevant but not loaded (e.g., modality active in this season)
              buttonClass += " border-teal-300 text-teal-500 hover:text-teal-600 hover:border-teal-400";
            } else {
              // Inactive state: not relevant or not loaded
              buttonClass += " border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300";
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
    </div>
  );
};

export default SeasonSelector;
