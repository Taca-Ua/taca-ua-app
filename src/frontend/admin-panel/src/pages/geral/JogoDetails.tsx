import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { matchesApi, type Match, type MatchUpdate } from '../../api/matches';
import { tournamentsApi, type Tournament } from '../../api/tournaments';
import { teamsApi, type Team } from '../../api/teams';

const JogoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [match, setMatch] = useState<Match | null>(null);
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editLocation, setEditLocation] = useState('');
  const [editStartTime, setEditStartTime] = useState('');
  const [editStatus, setEditStatus] = useState<'scheduled' | 'in_progress' | 'finished' | 'cancelled'>('scheduled');
  const [editScoreHome, setEditScoreHome] = useState('');
  const [editScoreAway, setEditScoreAway] = useState('');

  // Delete confirmation
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [matchData, teamsData] = await Promise.all([
        matchesApi.getById(Number(id)),
        teamsApi.getAll()
      ]);

      setMatch(matchData);
      setAllTeams(teamsData);

      // Fetch tournament info
      const tournamentData = await tournamentsApi.getById(matchData.tournament_id);
      setTournament(tournamentData);

      // Initialize edit fields
      setEditLocation(matchData.location);
      setEditStartTime(matchData.start_time);
      setEditStatus(matchData.status);
      setEditScoreHome(matchData.home_score?.toString() || '');
      setEditScoreAway(matchData.away_score?.toString() || '');

    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
        console.error(err);
      } else {
        setError('Erro ao carregar dados do jogo');
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const getTeamName = (teamId: number) => {
    const team = allTeams.find(t => t.id === teamId);
    return team?.name || `Equipa #${teamId}`;
  };

  const handleSaveEdit = async () => {
    if (!match) return;

    if (!editLocation.trim() || !editStartTime.trim()) {
      alert('Local e Data/Hora são obrigatórios');
      return;
    }

    try {
      setError('');

      const updateData: MatchUpdate = {
        location: editLocation,
        start_time: editStartTime,
        status: editStatus,
      };

      // Only include scores if status is finished and scores are provided
      if (editStatus === 'finished' && editScoreHome && editScoreAway) {
        updateData.home_score = Number(editScoreHome);
        updateData.away_score = Number(editScoreAway);
      }

      const updatedMatch = await matchesApi.update(match.id, updateData);
      setMatch(updatedMatch);
      setIsEditing(false);
      alert('Jogo atualizado com sucesso!');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
        console.error(err);
      } else {
        setError('Erro ao atualizar jogo');
        console.error(err);
      }
    }
  };

  const handleDelete = async () => {
    if (!match) return;

    try {
      setError('');
      await matchesApi.delete(match.id);
      alert('Jogo eliminado com sucesso!');
      navigate('/geral/torneios/' + match.tournament_id);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
        console.error(err);
      } else {
        setError('Erro ao eliminar jogo');
        console.error(err);
      }
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { label: string; color: string }> = {
      scheduled: { label: 'Agendado', color: 'bg-blue-100 text-blue-800' },
      in_progress: { label: 'Em Curso', color: 'bg-yellow-100 text-yellow-800' },
      finished: { label: 'Terminado', color: 'bg-green-100 text-green-800' },
      cancelled: { label: 'Cancelado', color: 'bg-red-100 text-red-800' },
    };
    const badge = badges[status] || badges.scheduled;
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="p-8 max-w-3xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="text-xl text-red-600 mb-4">Jogo não encontrado</div>
            <button
              onClick={() => navigate('/geral/dashboard')}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium"
            >
              Voltar ao Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="p-8 max-w-3xl mx-auto">
        {/* Back button */}
        <button
          onClick={() => navigate('/geral/torneios/' + match.tournament_id)}
          className="mb-6 flex items-center text-teal-600 hover:text-teal-700 font-medium transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Voltar ao Torneio
        </button>

        {/* Tournament context */}
        {tournament && (
          <div className="mb-4 text-gray-600">
            <span className="font-medium">Torneio:</span> {tournament.name}
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {/* Match Details Card */}
        <div className="bg-white rounded-lg shadow-md p-8">
          {!isEditing ? (
            <div className="space-y-6">
              {/* Teams Match Header */}
              <div className="text-center pb-6 border-b">
                <div className="flex justify-center items-center gap-8 mb-6">
                  <div className="text-2xl font-bold text-gray-800">{getTeamName(match.team_home_id)}</div>
                  <div className="text-3xl font-bold text-gray-400">VS</div>
                  <div className="text-2xl font-bold text-gray-800">{getTeamName(match.team_away_id)}</div>
                </div>

                {/* Score */}
                {match.status === 'finished' && match.home_score !== null && match.away_score !== null && (
                  <div className="text-5xl font-bold text-teal-600">
                    {match.home_score} - {match.away_score}
                  </div>
                )}
              </div>

              {/* Match Info */}
              <div className="space-y-4">
                <div>
                  <label className="block text-teal-500 font-medium mb-2">Estado</label>
                  <div className="bg-gray-100 px-4 py-3 rounded-md">
                    {getStatusBadge(match.status)}
                  </div>
                </div>
                <div>
                  <label className="block text-teal-500 font-medium mb-2">Local</label>
                  <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{match.location}</div>
                </div>
                <div>
                  <label className="block text-teal-500 font-medium mb-2">Data e Hora</label>
                  <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
                    {new Date(match.start_time).toLocaleString('pt-PT')}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 mt-8">
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                >
                  Editar
                </button>
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
                >
                  Eliminar
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Teams (non-editable) */}
              <div className="text-center p-4 bg-gray-50 rounded-md mb-6">
                <div className="flex justify-center items-center gap-8">
                  <div className="text-xl font-bold">{getTeamName(match.team_home_id)}</div>
                  <div className="text-2xl font-bold text-gray-400">VS</div>
                  <div className="text-xl font-bold">{getTeamName(match.team_away_id)}</div>
                </div>
                <p className="text-sm text-gray-500 mt-2">As equipas não podem ser alteradas</p>
              </div>

              {/* Status */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">Estado *</label>
                <select
                  className="border w-full px-4 py-2 rounded-md bg-white"
                  value={editStatus}
                  onChange={e => setEditStatus(e.target.value as 'scheduled' | 'in_progress' | 'finished' | 'cancelled')}
                >
                  <option value="scheduled">Agendado</option>
                  <option value="in_progress">Em Curso</option>
                  <option value="finished">Terminado</option>
                  <option value="cancelled">Cancelado</option>
                </select>
              </div>

              {/* Scores (only if finished) */}
              {editStatus === 'finished' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-teal-500 font-medium mb-2">
                      Golos/Pontos {getTeamName(match.team_home_id)}
                    </label>
                    <input
                      type="number"
                      min="0"
                      className="border w-full px-4 py-2 rounded-md"
                      value={editScoreHome}
                      onChange={e => setEditScoreHome(e.target.value)}
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-teal-500 font-medium mb-2">
                      Golos/Pontos {getTeamName(match.team_away_id)}
                    </label>
                    <input
                      type="number"
                      min="0"
                      className="border w-full px-4 py-2 rounded-md"
                      value={editScoreAway}
                      onChange={e => setEditScoreAway(e.target.value)}
                      placeholder="0"
                    />
                  </div>
                </div>
              )}

              {/* Location */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">Local *</label>
                <input
                  type="text"
                  className="border w-full px-4 py-2 rounded-md"
                  value={editLocation}
                  onChange={e => setEditLocation(e.target.value)}
                />
              </div>

              {/* Start Time */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">Data e Hora *</label>
                <input
                  type="datetime-local"
                  className="border w-full px-4 py-2 rounded-md"
                  value={editStartTime}
                  onChange={e => setEditStartTime(e.target.value)}
                />
              </div>

              {/* Actions */}
              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditLocation(match.location);
                    setEditStartTime(match.start_time);
                    setEditStatus(match.status);
                    setEditScoreHome(match.home_score?.toString() || '');
                    setEditScoreAway(match.away_score?.toString() || '');
                    setError('');
                  }}
                  className="flex-1 px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                >
                  Guardar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">Confirmar Eliminação</h2>
              <p className="mb-6 text-gray-600">
                Tem a certeza que deseja eliminar este jogo? Esta ação não pode ser revertida.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="flex-1 px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleDelete}
                  className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default JogoDetails;
