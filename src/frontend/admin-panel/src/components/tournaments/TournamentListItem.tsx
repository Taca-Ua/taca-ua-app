import { useNavigate } from 'react-router-dom';
import { type Tournament } from '../../api/tournaments';
import { TOURNAMENT_STATUS_LABELS, TOURNAMENT_STATUS_COLORS } from '../../constants/tournaments';

interface TournamentListItemProps {
  tournament: Tournament;
  showModality?: boolean; // Whether to show the modality name
  fromModalityId?: string; // If provided, adds return context to navigation
}

const TournamentListItem = ({ tournament, showModality = true, fromModalityId }: TournamentListItemProps) => {
  const navigate = useNavigate();

  const handleClick = () => {
    const url = fromModalityId
      ? `/geral/torneios/${tournament.id}?fromModality=${fromModalityId}`
      : `/geral/torneios/${tournament.id}`;
    navigate(url);
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 flex justify-between items-center focus:outline-none focus:ring-2 focus:ring-teal-500"
    >
      <div className="flex flex-col">
        <span className="font-medium text-gray-800">{tournament.name}</span>
        <span className="text-xs text-gray-500 mt-1">
          {tournament.start_date
            ? `Início: ${new Date(tournament.start_date).toLocaleDateString('pt-PT')}`
            : 'Data não definida'}
        </span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        {showModality && (
          <>
            <span className="text-teal-600 font-medium">{tournament.modality.name}</span>
            <span className="text-gray-400">|</span>
          </>
        )}
        <span
          className={`px-2 py-1 rounded-full font-medium ${
            TOURNAMENT_STATUS_COLORS[tournament.status] || 'bg-gray-100 text-gray-600'
          }`}
        >
          {TOURNAMENT_STATUS_LABELS[tournament.status] || tournament.status}
        </span>
      </div>
    </button>
  );
};

export default TournamentListItem;
