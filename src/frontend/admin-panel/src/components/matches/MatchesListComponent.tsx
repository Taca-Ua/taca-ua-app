import { useEffect, useState } from "react"
import { matchesApi, type MatchListItem } from "../../api/matches"
import { useNavigate } from "react-router-dom";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import { useAuth } from "../../hooks/useAuth";


const MatchesListItemComponent = ( { match, onDeleted } : { match: MatchListItem; onDeleted: () => void } ) => {
    const navigate = useNavigate();
    const { notify } = useNotification();
    const { isAdminGeneral } = useAuth();

    const getStatusText = (status: string) => {
        switch (status) {
            case 'scheduled': return 'Agendado';
            case 'in_progress': return 'Em Progresso';
            case 'finished': return 'Finalizado';
            case 'cancelled': return 'Cancelado';
            default: return status;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'scheduled': return 'bg-blue-100 text-blue-800';
            case 'in_progress': return 'bg-green-100 text-green-800';
            case 'finished': return 'bg-gray-100 text-gray-800';
            case 'cancelled': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getParticipantNames = (participants: MatchListItem['participants']): string => {
        const names = participants.map(p => {
            if (p.name) {
                return p.name;
            }
            return 'Desconecido';
        });
        return names.join(' vs ');
    };

    const getParticipantScores = (participants: MatchListItem['participants']): string | null => {
        if (participants.every(p => p.score !== null && p.score !== undefined)) {
            return participants.map(p => p.score).join(' - ');
        }
        return null;
    };

    const handleDelete = async () => {
        try {
            await matchesApi.delete(match.id);
            notify("Jogo eliminado com sucesso!", "success");
            if (onDeleted) onDeleted();
        } catch (error) {
            console.error("Error deleting match:", error);
            notify("Ocorreu um erro ao eliminar o jogo. Por favor, tente novamente.", "error");
        }
    };

    return (
      <button
        type="button"
        onClick={() => navigate(`/jogos/${match.id}`)}
        className="w-full text-left p-4 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
      >
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <div className="font-medium text-gray-800 mb-2">
              {getParticipantNames(match.participants)}
            </div>
            {getParticipantScores(match.participants) && (
              <div className="text-lg font-bold text-teal-600 mb-2">
                {getParticipantScores(match.participants)}
              </div>
            )}
            <div className="flex gap-4 text-sm text-gray-600">
              <span>{match.location}</span>
              <span>
                {new Date(match.start_time).toLocaleString("pt-PT", {
                  year: "numeric",
                  month: "2-digit",
                  day: "2-digit",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className="mt-2">
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}
              >
                {getStatusText(match.status)}
              </span>
            </div>
          </div>
          <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
            <Button
              onClick={handleDelete}
              type="danger"
              confirmation={{
                title: "Eliminar jogo",
                message: "Tem certeza que deseja eliminar este jogo?",
                confirmLabel: "Eliminar",
              }}
              flexible={true}
              padding="px-4 py-2"
              active={isAdminGeneral}
            >
              Eliminar
            </Button>
          </div>
        </div>
      </button>
    );
}

const MatchesListComponent = ( {
    matchesState,
    tournamentId
} : {
    matchesState?: [MatchListItem[], React.Dispatch<React.SetStateAction<MatchListItem[]>>];
    tournamentId?: string
} ) => {
    const [matches, setMatches] = matchesState ? matchesState : useState<MatchListItem[]>([]);
    const [loading, setLoading] = useState<boolean>( true );

    const [matchStatusFilter, setMatchStatusFilter] = useState<string>( 'all' );

    useEffect( () => {
        const fetchMatches = async () => {
            setLoading( true );
            try {
                const response = await matchesApi.getAll( {
                    tournament_id: tournamentId
                } );
                setMatches( response );
            } catch ( error ) {
                console.error( "Error fetching matches:", error );
            } finally {
                setLoading( false );
            }
        };
        fetchMatches();
    }, [ tournamentId ] );


    const filteredMatches = matches.filter( match => {
            if ( matchStatusFilter === 'all' ) return true;
            return match.status === matchStatusFilter;
        }
    );

    if ( loading ) {
        return <div>Loading matches...</div>;
    }

    return (
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800">
            Jogos ({filteredMatches.length})
          </h2>
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

        <div className="space-y-3">
          {filteredMatches.length > 0 ? (
            filteredMatches.map((match) =>
              <MatchesListItemComponent key={match.id} match={match} onDeleted={() => setMatches((prev) => prev.filter((m) => m.id !== match.id))} />)
          ) : (
            <p className="text-gray-500 text-center py-8">
              Nenhum jogo encontrado.
            </p>
          )}
        </div>
      </div>
    );
}

export default MatchesListComponent
