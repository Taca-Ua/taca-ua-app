import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import {
  matchesApi,
  type MatchDetail,
  type LineupDetail,
  type LineupAssign,
  type PlayerLineup
} from '../../api/matches';
import type { Team } from '../../api/teams';
import { tournamentsApi, type Tournament } from '../../api/tournaments';

// ==================== Private Components ====================

// Match Info Card Component
const MatchInfoCard = ({ match, tournament }: { match: MatchDetail; tournament: Tournament | null }) => {
  const formatDateTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return {
        date: date.toLocaleDateString('pt-PT'),
        time: date.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
      };
    } catch {
      return { date: dateString, time: '' };
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      scheduled: { label: 'Agendado', color: 'bg-blue-100 text-blue-800' },
      in_progress: { label: 'Em Curso', color: 'bg-yellow-100 text-yellow-800' },
      finished: { label: 'Terminado', color: 'bg-green-100 text-green-800' },
      cancelled: { label: 'Cancelado', color: 'bg-red-100 text-red-800' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.scheduled;

    return (
      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const { date, time } = formatDateTime(match.start_time);
  const participants = match.participants || [];

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="flex justify-center items-center gap-8 mb-8">
        {participants.slice(0, 2).map((participant, idx) => (
          <div key={participant.id}>
            <div className="w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-12 h-12 text-gray-700" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
              </svg>
            </div>
            <p className="text-center mt-2 text-sm font-medium text-gray-700 max-w-[120px] truncate">
              {participant.team?.name || participant.athlete?.full_name || 'Participante'}
            </p>
          </div>
        ))}
        {participants.length > 2 && (
          <div className="text-sm text-gray-500">
            +{participants.length - 2} mais
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-6">Detalhes do Jogo</h2>

        <div className="space-y-4">
          {tournament && (
            <div>
              <label className="block text-gray-600 text-sm mb-1">Torneio</label>
              <div className="text-gray-800 font-medium">{tournament.name}</div>
              {tournament.modality && (
                <div className="text-gray-500 text-sm">{tournament.modality.name}</div>
              )}
            </div>
          )}

          <div>
            <label className="block text-gray-600 text-sm mb-1">Estado</label>
            <div>{getStatusBadge(match.status)}</div>
          </div>

          <div>
            <label className="block text-gray-600 text-sm mb-1">Data e Hora</label>
            <div className="text-gray-800 font-medium">
              {date} às {time}
            </div>
          </div>

          <div>
            <label className="block text-gray-600 text-sm mb-1">Local</label>
            <div className="text-gray-800 font-medium">{match.location}</div>
          </div>

          {match.status === 'finished' && (
            <div>
              <label className="block text-gray-600 text-sm mb-1">Resultados</label>
              <div className="space-y-2">
                {participants.map((participant) => (
                  <div key={participant.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="text-gray-800 font-medium">
                      {participant.team?.name || participant.athlete?.full_name || 'Participante'}
                    </span>
                    <div className="flex gap-4 text-sm">
                      {participant.score !== null && participant.score !== undefined && (
                        <span className="text-teal-600 font-bold">
                          Pontuação: {participant.score}
                        </span>
                      )}
                      {participant.position !== null && participant.position !== undefined && (
                        <span className="text-teal-600 font-bold">
                          {participant.position}º Lugar
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Team Lineup Card Component
const TeamLineupCard = ({
  participant,
  lineups,
  canEdit,
  onEdit
}: {
  participant: MatchDetail['participants'][0];
  lineups: LineupDetail[];
  canEdit: boolean;
  onEdit: () => void;
}) => {
  const teamName = participant.team?.name || participant.athlete?.full_name || 'Participante';
  const teamLineups = lineups.filter(l => l.team_id === participant.team?.id);
  const starters = teamLineups.filter(l => l.is_starter);
  const bench = teamLineups.filter(l => !l.is_starter);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-gray-800">{teamName}</h3>
        {canEdit && (
          <button
            onClick={onEdit}
            className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md text-sm font-medium transition-colors"
          >
            Editar Convocatória
          </button>
        )}
      </div>

      {teamLineups.length === 0 ? (
        <p className="text-gray-500 text-center py-4">Nenhum jogador convocado.</p>
      ) : (
        <div className="space-y-4">
          {starters.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-600 mb-2">Titulares</p>
              <div className="space-y-2">
                {starters.map((lineup) => (
                  <div key={lineup.id} className="flex justify-between items-center p-3 bg-teal-50 rounded-md">
                    <span className="text-gray-800 font-medium">
                      {lineup.player?.full_name || 'Jogador'}
                    </span>
                    <span className="flex-shrink-0 w-8 h-8 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {lineup.jersey_number}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {bench.length > 0 && (
            <div>
              <p className="text-sm font-medium text-gray-600 mb-2">Suplentes</p>
              <div className="space-y-2">
                {bench.map((lineup) => (
                  <div key={lineup.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
                    <span className="text-gray-800 font-medium">
                      {lineup.player?.full_name || 'Jogador'}
                    </span>
                    <span className="flex-shrink-0 w-8 h-8 bg-gray-400 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {lineup.jersey_number}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Lineup Editor Modal Component
const LineupEditorModal = ({
  show,
  team,
  existingLineups,
  onSave,
  onClose
}: {
  show: boolean;
  team: Team | null;
  existingLineups: LineupDetail[];
  onSave: (players: PlayerLineup[]) => void;
  onClose: () => void;
}) => {
  const [selectedPlayers, setSelectedPlayers] = useState<PlayerLineup[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (show && team) {
      // Initialize with existing lineups
      const initial: PlayerLineup[] = existingLineups.map(lineup => ({
        player_id: lineup.player_id,
        jersey_number: lineup.jersey_number,
        is_starter: lineup.is_starter,
      }));
      setSelectedPlayers(initial);
    }
  }, [show, team, existingLineups]);

  if (!show || !team) return null;

  const togglePlayer = (playerId: string) => {
    const index = selectedPlayers.findIndex(p => p.player_id === playerId);
    if (index >= 0) {
      setSelectedPlayers(selectedPlayers.filter(p => p.player_id !== playerId));
    } else {
      setSelectedPlayers([...selectedPlayers, { player_id: playerId, jersey_number: 1, is_starter: false }]);
    }
  };

  const updatePlayer = (playerId: string, field: 'jersey_number' | 'is_starter', value: number | boolean) => {
    setSelectedPlayers(selectedPlayers.map(p =>
      p.player_id === playerId ? { ...p, [field]: value } : p
    ));
  };

  const handleSave = () => {
    onSave(selectedPlayers);
    setSearchQuery('');
  };

  const handleCancel = () => {
    setSearchQuery('');
    onClose();
  };

  const filteredPlayers = team.players?.filter(player =>
    player.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Editar Convocatória - {team.name}
        </h2>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Procurar jogadores..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
        </div>

        <div className="space-y-2 max-h-[500px] overflow-y-auto mb-6">
          {filteredPlayers.length > 0 ? (
            filteredPlayers.map((player) => {
              const lineupEntry = selectedPlayers.find(p => p.player_id === player.id);
              const isSelected = !!lineupEntry;

              return (
                <div key={player.id} className="px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors">
                  <div className="flex items-center gap-3 mb-2">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => togglePlayer(player.id)}
                      className="w-5 h-5 text-teal-500 rounded focus:ring-2 focus:ring-teal-500"
                    />
                    <span className="text-gray-800 flex-1 font-medium">{player.full_name}</span>
                  </div>
                  {isSelected && lineupEntry && (
                    <div className="ml-8 flex gap-4 items-center">
                      <div className="flex items-center gap-2">
                        <label className="text-sm text-gray-600">Número:</label>
                        <input
                          type="number"
                          min="1"
                          max="99"
                          value={lineupEntry.jersey_number}
                          onChange={(e) => updatePlayer(player.id, 'jersey_number', parseInt(e.target.value) || 1)}
                          className="w-16 px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                        />
                      </div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={lineupEntry.is_starter}
                          onChange={(e) => updatePlayer(player.id, 'is_starter', e.target.checked)}
                          className="w-4 h-4 text-teal-500 rounded focus:ring-2 focus:ring-teal-500"
                        />
                        <span className="text-sm text-gray-600">Titular</span>
                      </label>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <p className="text-gray-500 text-center py-4">
              {searchQuery ? 'Nenhum jogador encontrado.' : 'Nenhum jogador disponível.'}
            </p>
          )}
        </div>

        <div className="flex gap-4">
          <button
            onClick={handleCancel}
            className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

// ==================== Main Component ====================

const MatchDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [lineups, setLineups] = useState<LineupDetail[]>([]);
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal state
  const [showLineupModal, setShowLineupModal] = useState(false);
  const [editingParticipant, setEditingParticipant] = useState<MatchDetail['participants'][0] | null>(null);

  useEffect(() => {
    fetchMatchData();
  }, [id]);

  const fetchMatchData = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError('');

      const [matchData, lineupsData] = await Promise.all([
        matchesApi.getById(id),
        matchesApi.getLineups(id),
      ]);

      setMatch(matchData);
      setLineups(lineupsData);

      // Fetch tournament details
      if (matchData.tournament_id) {
        try {
          const tournamentData = await tournamentsApi.getById(matchData.tournament_id);
          setTournament(tournamentData);
        } catch {
          // Tournament not critical, ignore error
        }
      }
    } catch (err) {
      console.error('Error loading match data:', err);
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados do jogo');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenLineupEditor = (participant: MatchDetail['participants'][0]) => {
    if (!participant.team) {
      alert('Este participante não é uma equipa.');
      return;
    }

    setEditingParticipant(participant);
    setShowLineupModal(true);
  };

  const handleSaveLineup = async (players: PlayerLineup[]) => {
    if (!match || !editingParticipant?.team) return;

    try {
      setError('');

      const lineupData: LineupAssign = {
        team_id: editingParticipant.team.id,
        players: players,
      };

      await matchesApi.assignLineup(match.id, lineupData);
      setShowLineupModal(false);
      setEditingParticipant(null);

      // Refresh lineups
      const updatedLineups = await matchesApi.getLineups(match.id);
      setLineups(updatedLineups);

      alert('Convocatória guardada com sucesso!');
    } catch (err) {
      console.error('Error saving lineup:', err);
      setError(err instanceof Error ? err.message : 'Erro ao guardar convocatória');
    }
  };

  const handleDownloadMatchSheet = async () => {
    if (!match) return;

    try {
      setError('');
      const blob = await matchesApi.getMatchSheet(match.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ficha-jogo-${match.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading match sheet:', err);
      setError(err instanceof Error ? err.message : 'Erro ao descarregar ficha de jogo');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="flex-1 flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="flex-1 p-8 max-w-4xl mx-auto">
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded">
            <p className="font-bold">Jogo não encontrado</p>
            <p className="text-sm mt-1">O jogo que procura não existe ou foi removido.</p>
          </div>
        </div>
      </div>
    );
  }

  const canEditLineups = match.status === 'scheduled';
  const teamParticipants = match.participants.filter(p => p.team);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="mb-6 flex items-center text-teal-600 hover:text-teal-700 font-medium transition-colors group"
          >
            <svg
              className="w-5 h-5 mr-2 transform group-hover:-translate-x-1 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Voltar
          </button>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-md flex items-start">
              <svg className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <MatchInfoCard match={match} tournament={tournament} />

              <div className="mt-6 space-y-3">
                <button
                  onClick={handleDownloadMatchSheet}
                  className="w-full px-4 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-md font-medium transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Descarregar Ficha de Jogo
                </button>

                {!canEditLineups && (
                  <div className="px-4 py-3 bg-gray-100 text-gray-600 rounded-md text-sm text-center">
                    Não pode editar convocatórias após o início do jogo
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-2 space-y-6">
              {teamParticipants.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <p className="text-gray-500">Nenhuma equipa participante neste jogo.</p>
                </div>
              ) : (
                teamParticipants.map((participant) => (
                  <TeamLineupCard
                    key={participant.id}
                    participant={participant}
                    lineups={lineups}
                    canEdit={canEditLineups}
                    onEdit={() => handleOpenLineupEditor(participant)}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <LineupEditorModal
        show={showLineupModal}
        team={editingParticipant?.team || null}
        existingLineups={lineups.filter(l => l.team_id === editingParticipant?.team?.id)}
        onSave={handleSaveLineup}
        onClose={() => {
          setShowLineupModal(false);
          setEditingParticipant(null);
        }}
      />
    </div>
  );
};

export default MatchDetail;
