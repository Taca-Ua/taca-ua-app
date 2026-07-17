import { useEffect, useState } from "react";
import { type GeneralRankingListItem, rankingApi } from "../../api/ranking";
import { modalitiesApi, type ModalityListItem } from "../../api/modalities";
import { useSeason } from "../../contexts/SeasonContext";
import { useNotification } from "../../contexts/NotificationProvider";
import { Link } from "react-router-dom";
import LazyImage from "../utils/LazyImage";

const GeneralRankingListItemComponent = ({
    item,
    position
} : {
    item: GeneralRankingListItem
    position: number
}) => {


    const getPodiumBgClass = (position: number | null | undefined) => {
    if (!position) return "bg-gray-50 hover:bg-gray-100";
    switch (position) {
      case 1:
        return "bg-yellow-100 hover:bg-yellow-200 border-2 border-yellow-400";
      case 2:
        return "bg-gray-100 hover:bg-gray-200 border-2 border-gray-400";
      case 3:
        return "bg-orange-100 hover:bg-orange-200 border-2 border-orange-400";
      default:
        return "bg-gray-50 hover:bg-gray-100";
    }
  };

    const renderPositionBadge = () => {
        switch (position) {
            case 0:
                return <span className="font-bold text-xl min-w-10 h-10 flex items-center justify-center rounded-full text-white" style={{ backgroundColor: '#FFD700', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>1º</span>;
            case 1:
                return <span className="font-bold text-xl min-w-10 h-10 flex items-center justify-center rounded-full text-white" style={{ backgroundColor: '#C0C0C0', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>2º</span>;
            case 2:
                return <span className="font-bold text-xl min-w-10 h-10 flex items-center justify-center rounded-full text-white" style={{ backgroundColor: '#CD7F32', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>3º</span>;
            default:
                return <span className="font-bold text-xl min-w-10 h-10 flex items-center justify-center rounded-full text-white" style={{ backgroundColor: '#ccc', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>{position + 1}º</span>;
        }
    }

    return (
        <Link
            to={`/cursos/${item.course.id}`}
            className={"cursor-pointer bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200 p-6 px-8 flex flex-col gap-4" + getPodiumBgClass(position + 1)}
        >
            <div className="flex text-center items-center justify-between justify-items-stretch gap-4">
              {renderPositionBadge()}
              <div className="flex-1 flex flex-col items-center justify-center gap-1">
                {item.course.logo_url ? (
                  <LazyImage src={item.course.logo_url} alt={item.course.name} className="h-24 object-cover" />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-teal-50 flex items-center justify-center border-2 border-teal-500">
                    <span className="text-teal-600 font-bold text-sm">{item.course.name.charAt(0)}</span>
                  </div>
                )}
                <span className="text-gray-800 font-medium text-sm block">{item.course.name}</span>
              </div>
              <div className="flex-1">
                  <span className="text-gray-800 font-bold text-4xl block">{item.points}</span>
                  <span className="text-gray-500 text-sm block mt-4">Pontos Extra</span>
                  <span className={"text-gray-800 font-medium text-lg block" + (item.extra_points > 0 ? " text-green-600" : item.extra_points < 0 ? " text-red-600" : "")}>
                      {item.extra_points > 0 && "+"}
                      {item.extra_points}
                  </span>
              </div>
            </div>
        </Link>
    );
}


const GeneralRankingListComponent = ({
    rankingState,
} : {
    rankingState?: [GeneralRankingListItem[], React.Dispatch<React.SetStateAction<GeneralRankingListItem[]>>]
}) => {
    const { loadedSeason } = useSeason();
    const { notify } = useNotification();

    const [ranking, setRanking] = rankingState ?? useState<GeneralRankingListItem[]>([]);
    const [expanded, setExpanded] = useState(false);

    const [modalities, setModalities] = useState<ModalityListItem[] | null>(null);
    const [selectedModalityIndex, setSelectedModalityIndex] = useState<number>(-1);

    useEffect(() => {
        if (!loadedSeason) return;

        rankingApi.getGeneralRanking(loadedSeason.id, {
          modality_id: selectedModalityIndex >= 0 ? modalities?.[selectedModalityIndex]?.id : undefined
        }).then((ranking) => {
            setRanking(ranking);
        }).catch((error) => {
            notify("Falha ao carregar o ranking geral.", "error");
            console.error("Error fetching general ranking:", error);
        })
    }, [loadedSeason, selectedModalityIndex]);

    useEffect(() => {
        if (!loadedSeason) return;

        modalitiesApi.getAll({season_id: loadedSeason.id}).then((modalities) => {
            setModalities(modalities);
        }).catch((error) => {
            notify("Falha ao carregar as modalidades.", "error");
            console.error("Error fetching modalities:", error);
        })
    }, [loadedSeason]);

    const displayedRanking = expanded ? ranking : ranking.slice(0, 6);

    return (
      <div className="flex-1 max-w-7xl mx-auto overflow-x-auto bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          {/* Left Arrow */}
          <button
            onClick={() => setSelectedModalityIndex((prevIndex) => Math.max(prevIndex - 1, -1))}
            disabled={!modalities || modalities.length === 0 || selectedModalityIndex <= -1}
            className={`px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition-colors ${!modalities || modalities.length === 0 || selectedModalityIndex <= -1 ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 inline-block mr-2 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Modality Name */}
          <span className="text-xl font-semibold text-gray-800">
            {selectedModalityIndex >= 0 && modalities ? modalities[selectedModalityIndex].name : "Ranking Geral"}
          </span>

          {/* Right Arrow */}
          <button
            onClick={() => setSelectedModalityIndex((prevIndex) => (prevIndex + 1))}
            disabled={!modalities || modalities.length === 0 || selectedModalityIndex >= modalities.length - 1}
            className={`px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition-colors ${!modalities || modalities.length === 0 || selectedModalityIndex >= modalities.length - 1 ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 inline-block ml-2 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedRanking.map((item, index) => (
            <GeneralRankingListItemComponent key={item.course.id} item={item} position={index} />
          ))}
        </div>
        <div className="mt-4 flex justify-center">
          <button
            onClick={() => setExpanded(!expanded)}
            className="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition-colors"
          >
            {expanded ? "Ver menos" : "Ver mais"}
          </button>
        </div>
      </div>
    );
};

export default GeneralRankingListComponent;
