import { useState } from "react";
import { matchesApi, type MatchListItem } from "../../../../api/matches"
import { normalizeText } from "../../../utils/utils";
import { MatchesListItemComponent } from "../../../matches/MatchesListComponent";
import Button from "../../../utils/Button";
import { useModal } from "../../../../contexts/ModalContext";
import { useAuth } from "../../../../hooks/useAuth";
import TornLeagueMatchSugestionConfigModal from "./TornLeagueMatchSugestionConfigModal";
import type { TournamentDetail } from "../../../../api/tournaments";

interface TornLeagueMatchListItem extends MatchListItem {
    format_specific_data: {
        round_number: number;
    };
}

const MatchesJourneyComponent = ({
    matches,
    journeyNumber,
    onMatchDeleted
} : {
    matches: TornLeagueMatchListItem[],
    journeyNumber: number,
    onMatchDeleted?: (matchId: string) => void
}) => {
    const [isExpanded, setIsExpanded] = useState<boolean>(false);

    const relevantMatches = matches.filter(match => match.format_specific_data?.round_number === journeyNumber);

    const handleToggle = () => {
        setIsExpanded(!isExpanded);
    };

    return (
      <div>
        <div
          className="flex justify-between items-center cursor-pointer bg-gray-200 px-4 py-2 rounded-md"
          onClick={() => handleToggle()}
        >
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-700">
              Jornada {journeyNumber}
            </h3>
            <p className="text-sm text-gray-500">
              {relevantMatches.length} jogo
              {relevantMatches.length !== 1 ? "s" : ""}
            </p>
          </div>
          <span className="text-gray-500">
            {isExpanded ? "Ocultar" : "Mostrar"}
          </span>
        </div>
        {isExpanded && (
          <div className="mt-3 space-y-3">
            {relevantMatches.map((match) => (
              <MatchesListItemComponent
                key={match.id}
                match={match}
                onDeleted={() => onMatchDeleted && onMatchDeleted(match.id)}
              />
            ))}
          </div>
        )}
      </div>
    );
};


const TornLeagueMatchesDisplay = ({
    tournament,
    matchesState
} : {
    tournament: TournamentDetail,
    matchesState: [MatchListItem[], React.Dispatch<React.SetStateAction<MatchListItem[]>>]
}) => {
    const { pushModal } = useModal();
    const { isAdminGeneral } = useAuth();

    const [matches, setMatches] = matchesState;
    const [matchStatusFilter, setMatchStatusFilter] = useState<string>( 'all' );
    const [query, setQuery] = useState<string>( '' );

    const handleMatchesRefresh = () => {
      matchesApi.getAll({tournament_id: tournament.id}).then((response) => {
        setMatches(response.matches);
      }).catch((error) => {
        console.error("Error fetching matches:", error);
      });
    };

    const handleMatchDeleted = (matchId: string) => {
        const updatedMatches = matches.filter(match => match.id !== matchId);
        setMatches(updatedMatches);
    };

    // Convert matches to TornLeagueMatchListItem type
    const tornLeagueMatches = matches.map(match => {
        const formatSpecificData = match.format_specific_data as { round_number: number } | undefined;
        return {
            ...match,
            format_specific_data: { round_number: formatSpecificData ? formatSpecificData.round_number : 0 }
        } as TornLeagueMatchListItem;
    });

    const filteredMatches = tornLeagueMatches.filter( match => {
            if ( matchStatusFilter === 'all' ) return true;
            return match.status === matchStatusFilter;
        }
    ).filter( match => {
        const participantNames = match.participants.map( p => normalizeText( p.name ) ).join( ' ' ).toLowerCase();
        const location = match.location ? normalizeText( match.location ) : '';
        const searchQuery = normalizeText( query ).toLowerCase();
        return participantNames.includes( searchQuery ) || location.includes( searchQuery );
    } ) as TornLeagueMatchListItem[];

    return (
      <div>
        <div className="flex mb-4">
          <Button
            onClick={() =>
              pushModal(
                <TornLeagueMatchSugestionConfigModal
                  tournamentId={tournament.id}
                  onMatchesCreated={handleMatchesRefresh}
                />,
              )
            }
            active={isAdminGeneral && tournament.competitors.length >= 2}
            flexible={true}
          >
            + Gerar Jogos
          </Button>
        </div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800">
            Jogos ({filteredMatches.length})
          </h2>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3">
              <select
                value={matchStatusFilter}
                onChange={(e) => setMatchStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="all">Todos os estados</option>
                <option value="scheduled">Agendados</option>
                <option value="in_progress">Em Progresso</option>
                <option value="finished">Finalizados</option>
                <option value="cancelled">Cancelados</option>
              </select>
            </div>
          </div>
        </div>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Pesquisar por local ou participantes..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
        </div>

        <div className="space-y-3">
          {filteredMatches.length > 0 ? (
            Array.from(
              new Set(
                filteredMatches.map(
                  (match) => match.format_specific_data.round_number,
                ),
              ),
            )
              .sort((a, b) => a - b)
              .map((round) => (
                <MatchesJourneyComponent
                  key={round}
                  matches={filteredMatches}
                  journeyNumber={round}
                  onMatchDeleted={handleMatchDeleted}
                />
              ))
          ) : (
            <p className="text-gray-500 text-sm">Nenhum jogo encontrado.</p>
          )}
        </div>
      </div>
    );
}

export default TornLeagueMatchesDisplay
