import { type Tournament } from '../../api/tournaments';
import { type Season } from '../../api/seasons';
import { TOURNAMENT_STATUS_ORDER } from '../../constants/tournaments';
import TournamentListItem from './TournamentListItem';

interface TournamentListProps {
  tournaments: Tournament[];
  loading?: boolean;
  searchQuery?: string;
  showModality?: boolean; // Whether to show modality in list items
  emptyMessage?: string;
  fromModalityId?: string; // If provided, adds return context to navigation
  seasons?: Season[];
}

const TournamentList = ({
  tournaments,
  loading = false,
  searchQuery = '',
  showModality = true,
  emptyMessage = 'Nenhum torneio encontrado.',
  fromModalityId,
  seasons = [],
}: TournamentListProps) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
        <p className="mt-2 text-gray-600">A carregar...</p>
      </div>
    );
  }

  if (tournaments.length === 0) {
    return <p className="text-gray-500 text-center py-8">{emptyMessage}</p>;
  }

  // Sort tournaments by status, modality (if shown), and name
  const sortedTournaments = [...tournaments].sort((a, b) => {
    const statusComparison =
      (TOURNAMENT_STATUS_ORDER[a.status] ?? 999) - (TOURNAMENT_STATUS_ORDER[b.status] ?? 999);
    if (statusComparison !== 0) return statusComparison;

    if (showModality) {
      const modalityComparison = a.modality.name.localeCompare(b.modality.name);
      if (modalityComparison !== 0) return modalityComparison;
    }

    return a.name.localeCompare(b.name);
  });

  return (
    <div className="space-y-3">
      {sortedTournaments.map((tournament) => (
        <TournamentListItem
          key={tournament.id}
          tournament={tournament}
          showModality={showModality}
          fromModalityId={fromModalityId}
          seasonYear={seasons.find(s => s.id === tournament.season_id)?.year ?? null}
        />
      ))}
    </div>
  );
};

export default TournamentList;
