import { useEffect, useState } from "react";
import { type TournamentListItem, tournamentsApi } from "../../api/tournaments";
import {
  TOURNAMENT_STATUS_COLORS,
  TOURNAMENT_STATUS_LABELS,
  TOURNAMENT_STATUS_ORDER,
} from "../../constants/tournaments";
import { useNavigate } from "react-router-dom";

const TournamentListItemComponent = ({
  tournament,
  showModality = true,
  fromModalityId,
}: {
  tournament: TournamentListItem;
  showModality?: boolean;
  fromModalityId?: string;
}) => {
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
            ? `Início: ${new Date(tournament.start_date).toLocaleDateString("pt-PT")}`
            : "Data não definida"}
        </span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        {showModality && (
          <>
            <span className="text-teal-600 font-medium">
              {tournament.modality.name}
            </span>
            <span className="text-gray-400">|</span>
          </>
        )}
        <span
          className={`px-2 py-1 rounded-full font-medium ${
            TOURNAMENT_STATUS_COLORS[tournament.status] ||
            "bg-gray-100 text-gray-600"
          }`}
        >
          {TOURNAMENT_STATUS_LABELS[tournament.status] || tournament.status}
        </span>
      </div>
    </button>
  );
};

const TournamentList = ({
  tournamentsState,
  showModality = true,
  fromModalityId,
  loadTournaments,
}: {
  tournamentsState?: [TournamentListItem[], React.Dispatch<React.SetStateAction<TournamentListItem[]>>];
  showModality?: boolean;
  fromModalityId?: string;
  loadTournaments?: () => Promise<TournamentListItem[]>;
}) => {
  const [tournaments, setTournaments] = tournamentsState
    ? tournamentsState
    : useState<TournamentListItem[]>([]);
  const [loading, setLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [modalityFilter, setModalityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const fetchTournaments = async () => {
      setLoading(true);
      try {
        const data = await (loadTournaments || tournamentsApi.getAll)();
        setTournaments(data);
      } catch (error) {
        console.error("Erro ao carregar torneios:", error);
        setTournaments([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, []);

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
        <p className="mt-2 text-gray-600">A carregar...</p>
      </div>
    );
  }

  if (tournaments.length === 0) {
    return <p className="text-gray-500 text-center py-8">Nenhum torneio encontrado. Crie um novo torneio para começar!</p>;
  }

  // Filter tournaments based on search query
  const uniqueModalities = Array.from(
    new Set(tournaments.map((t) => t.modality.id))
  ).map((id) => tournaments.find((t) => t.modality.id === id)?.modality)
    .filter((m): m is NonNullable<typeof m> => m !== undefined);

  const filteredTournaments = tournaments.filter((tournament) =>
    tournament.name.toLowerCase().includes(searchQuery.toLowerCase()),
  ).filter((tournament) =>
    modalityFilter ? tournament.modality.id === modalityFilter : true
  ).filter((tournament) =>
    statusFilter ? tournament.status === statusFilter : true
  );

  if (filteredTournaments.length === 0) {
    return (
      <p className="text-gray-500 text-center py-8">
        Nenhum torneio encontrado para "{searchQuery}".
      </p>
    );
  }

  // Sort tournaments by status, modality (if shown), and name
  const sortedTournaments = [...filteredTournaments].sort((a, b) => {
    const statusComparison =
      (TOURNAMENT_STATUS_ORDER[a.status] ?? 999) -
      (TOURNAMENT_STATUS_ORDER[b.status] ?? 999);
    if (statusComparison !== 0) return statusComparison;

    if (showModality) {
      const modalityComparison = a.modality.name.localeCompare(b.modality.name);
      if (modalityComparison !== 0) return modalityComparison;
    }

    return a.name.localeCompare(b.name);
  });

  return (
    <div className="bg-white shadow-md rounded-lg p-6 mt-6 space-y-3">
      {/* Search and Filters */}
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Pesquisar torneio..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
        />

        {showModality && (
          <select
            value={modalityFilter}
            onChange={(e) => setModalityFilter(e.target.value)}
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

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
        >
          <option value="">Todos os estados</option>
          <option value="draft">Rascunho</option>
          <option value="active">Ativo</option>
          <option value="finished">Finalizado</option>
        </select>
      </div>

      {/* Tournament List */}
      <div className="space-y-3">
        {sortedTournaments.map((tournament) => (
          <TournamentListItemComponent
            key={tournament.id}
            tournament={tournament}
            showModality={showModality}
            fromModalityId={fromModalityId}
          />
        ))}
      </div>
    </div>
  );
};

export default TournamentList;
