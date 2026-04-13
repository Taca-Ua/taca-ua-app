import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  matchesApi,
  type MatchList,
  type MatchListFilter,
} from "../../api/matches";
import { btn } from '../../styles/buttonStyles';

const ListMatchesComponent = ({ tournamentId }: { tournamentId?: string }) => {
  const navigate = useNavigate();

  const [matches, setMatches] = useState<MatchList[]>([]);
  const [matchStatusFilter, setMatchStatusFilter] = useState<string>('all');

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const data = await matchesApi.getAll({
          tournament_id: tournamentId,
        });
        setMatches(data);
      } catch (error) {
        console.error("Error fetching matches:", error);
      }
    };
    fetchMatches();
  }, [tournamentId]);

  // render functions
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

  const getParticipantNames = (participants: MatchList['participants']): string => {
    const names = participants.map(p => {
      if (p.name) {
        return p.name;
      }
      return 'Desconhecido';
    });
    return names.join(' vs ');
  };

  const getParticipantScores = (participants: MatchList['participants']): string | null => {
    if (participants.every(p => p.score !== null && p.score !== undefined)) {
      return participants.map(p => p.score).join(' - ');
    }
    return null;
  };

  const filteredMatches = matches.filter(match => {
    if (matchStatusFilter === 'all') return true;
    return match.status === matchStatusFilter;
  });

  if (filteredMatches.length === 0) {
    return <p>Nenhum jogo encontrado</p>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
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
          {/* <button
            onClick={() => {
              setShowCreateModal(true);
              resetForm();
            }}
            disabled={tournament.competitors.length < 2}
            className={`px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
            title={
              tournament.competitors.length < 2
                ? "É necessário pelo menos 2 competidores"
                : ""
            }
          >
            + Criar Jogo
          </button> */}
        </div>
      </div>

      <div className="space-y-3">
        {filteredMatches.map((match) => (
          <button
            key={match.id}
            type="button"
            onClick={() => navigate(`/geral/jogos/${match.id}`)}
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
                {/* <button
                  type="button"
                  onClick={() => handleDeleteMatch(match.id)}
                  className={`px-3 py-1 ${btn.dangerLight} rounded-md text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-red-400`}
                >
                  Eliminar
                </button> */}
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">
              Criar Jogo
            </h2>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-gray-700 font-medium">
                    Participantes{" "}
                    <HelpTooltip
                      text="Selecione os competidores que vão disputar este jogo. São necessários no mínimo 2 participantes. Só podem ser selecionados competidores já inscritos no torneio."
                      className="ml-1"
                    />{" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={addParticipantSlot}
                    className={`text-sm px-3 py-1 ${btn.info} rounded-md transition-colors`}
                  >
                    + Adicionar Participante
                  </button>
                </div>
                <div className="space-y-2">
                  {selectedParticipants.map((participantId, index) => (
                    <div key={index} className="flex gap-2">
                      <select
                        value={participantId}
                        onChange={(e) =>
                          updateParticipant(index, e.target.value)
                        }
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                      >
                        <option value="">Selecione um participante</option>
                        {tournament.competitors.map((competitor) => {
                          const isTeam = competitor.competitor_type === "team";
                          const id = isTeam
                            ? competitor.team?.id
                            : competitor.athlete?.id;
                          const name = isTeam
                            ? competitor.team?.name
                            : competitor.athlete?.full_name;
                          const label = isTeam ? name : `${name} (Atleta)`;

                          return (
                            <option
                              key={`${competitor.competitor_type}-${id}`}
                              value={id}
                            >
                              {label}
                            </option>
                          );
                        })}
                      </select>
                      {selectedParticipants.length > 2 && (
                        <button
                          type="button"
                          onClick={() => removeParticipantSlot(index)}
                          className={`px-3 py-2 ${btn.dangerLight} rounded-md transition-colors`}
                          title="Remover participante"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Mínimo de 2 participantes necessários
                </p>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Local{" "}
                  <HelpTooltip
                    text="Local onde o jogo vai decorrer, ex: Campo Municipal, Pavilhão Principal. Esta informação é visível aos participantes."
                    className="ml-1"
                  />{" "}
                  <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Ex: Campo Municipal"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Data e Hora <span className="text-red-500">*</span>
                </label>
                <input
                  type="datetime-local"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                disabled={loading}
                className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateMatch}
                disabled={loading}
                className={`flex-1 px-4 py-2 ${btn.primary} rounded-md disabled:opacity-50`}
              >
                {loading ? "A criar..." : "Criar"}
              </button>
            </div>
          </div>
        </div>
      )} */}

      {/* <ConfirmModal
        isOpen={matchToDelete !== null}
        title="Eliminar jogo"
        message="Tem certeza que deseja eliminar este jogo?"
        confirmLabel="Eliminar"
        variant="danger"
        loading={deletingMatch}
        onCancel={() => {
          if (!deletingMatch) {
            setMatchToDelete(null);
          }
        }}
        onConfirm={confirmDeleteMatch}
      /> */}
    </div>
  );
};

export default ListMatchesComponent;
