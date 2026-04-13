import { type Tournament } from '../../api/tournaments';
import { type Season } from '../../api/seasons';

interface TournamentFiltersProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusChange: (value: string) => void;
  modalityFilter?: string;
  onModalityChange?: (value: string) => void;
  availableTournaments?: Tournament[]; // To extract unique modalities
  showModalityFilter?: boolean;
  seasonFilter?: string;
  onSeasonChange?: (value: string) => void;
  availableSeasons?: Season[];
}

const TournamentFilters = ({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  modalityFilter = '',
  onModalityChange,
  availableTournaments = [],
  showModalityFilter = true,
  seasonFilter = '',
  onSeasonChange,
  availableSeasons = [],
}: TournamentFiltersProps) => {
  // Extract unique modalities from tournaments
  const uniqueModalities = showModalityFilter
    ? [...new Map(availableTournaments.map((t) => [t.modality.id, t.modality])).values()].sort(
        (a, b) => a.name.localeCompare(b.name)
      )
    : [];

  return (
    <div className="flex gap-3">
      <input
        type="text"
        placeholder="Pesquisar torneio..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
      />

      {showModalityFilter && onModalityChange && (
        <select
          value={modalityFilter}
          onChange={(e) => onModalityChange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
        >
          <option value="">Todas as modalidades</option>
          {uniqueModalities.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      )}

      {availableSeasons.length > 0 && onSeasonChange && (
        <select
          value={seasonFilter}
          onChange={(e) => onSeasonChange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
        >
          <option value="">Todas as épocas</option>
          {availableSeasons.map((s) => (
            <option key={s.id} value={s.id}>
              {s.year}{s.status === 'active' ? ' (ativa)' : s.status === 'draft' ? ' (rascunho)' : ' (finalizada)'}
            </option>
          ))}
        </select>
      )}

      <select
        value={statusFilter}
        onChange={(e) => onStatusChange(e.target.value)}
        className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
      >
        <option value="">Todos os estados</option>
        <option value="draft">Rascunho</option>
        <option value="active">Ativo</option>
        <option value="finished">Finalizado</option>
      </select>
    </div>
  );
};

export default TournamentFilters;
