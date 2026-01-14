import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { tournamentsApi, type TournamentDetail, type TournamentUpdate } from '../../api/tournaments';
import { teamsApi, type Team } from '../../api/teams';
import { matchesApi, type Match, type MatchCreate } from '../../api/matches';

// Component to display tournament information
const TournamentInfo = ({
  tournament,
  onEdit,
  onDelete
}: {
  tournament: TournamentDetail;
  onEdit: () => void;
  onDelete: () => void;
}) => {
  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'finished': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Ativo';
      case 'draft': return 'Rascunho';
      case 'finished': return 'Finalizado';
      default: return status;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Informação do Torneio</h2>

      <div>
        <label className="block text-teal-500 font-medium mb-2">Nome</label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
          {tournament.name}
        </div>
      </div>

      <div>
        <label className="block text-teal-500 font-medium mb-2">Modalidade</label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
          {tournament.modality.name}
        </div>
      </div>

      <div>
        <label className="block text-teal-500 font-medium mb-2">Estado</label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeColor(tournament.status)}`}>
            {getStatusText(tournament.status)}
          </span>
        </div>
      </div>

      {tournament.start_date && (
        <div>
          <label className="block text-teal-500 font-medium mb-2">Data de Início</label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
            {new Date(tournament.start_date).toLocaleDateString('pt-PT')}
          </div>
        </div>
      )}

      <div className="flex gap-4 pt-4">
        <button
          onClick={onEdit}
          className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
        >
          Editar
        </button>
        <button
          onClick={onDelete}
          className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
        >
          Eliminar
        </button>
      </div>
    </div>
  );
};

// Component for editing tournament
const EditTournamentModal = ({
  tournament,
  onClose,
  onSave
}: {
  tournament: TournamentDetail;
  onClose: () => void;
  onSave: (data: TournamentUpdate) => Promise<void>;
}) => {
  const [name, setName] = useState(tournament.name);
  const [startDate, setStartDate] = useState(
    tournament.start_date ? tournament.start_date.split('T')[0] : ''
  );
  const [status, setStatus] = useState<'draft' | 'active' | 'finished'>(
    tournament.status as 'draft' | 'active' | 'finished'
  );
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError('Nome é obrigatório');
      return;
    }

    try {
      setSaving(true);
      await onSave({
        name: name.trim(),
        start_date: startDate || undefined,
        status
      });
      onClose();
    } catch (err) {
      setError('Erro ao atualizar torneio');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Torneio</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Data de Início</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Estado</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as 'draft' | 'active' | 'finished')}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="draft">Rascunho</option>
              <option value="active">Ativo</option>
              <option value="finished">Finalizado</option>
            </select>
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={onClose}
            disabled={saving}
            className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md disabled:opacity-50"
          >
            {saving ? 'A guardar...' : 'Guardar'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Component to manage teams in tournament
const TournamentTeams = ({
  tournament,
  onTeamsChange
}: {
  tournament: TournamentDetail;
  onTeamsChange: () => void;
}) => {
  const [availableTeams, setAvailableTeams] = useState<Team[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAvailableTeams();
  }, [tournament]);

  const loadAvailableTeams = async () => {
    try {
      const allTeams = await teamsApi.getAll({ modality_id: tournament.modality.id });
      // Filter out teams already in tournament
      const teamIds = new Set(tournament.teams.map(t => t.id));
      setAvailableTeams(allTeams.filter(t => !teamIds.has(t.id)));
    } catch (err) {
      console.error('Failed to load teams:', err);
    }
  };

  const handleAddTeam = async () => {
    if (!selectedTeamId) {
      setError('Selecione uma equipa');
      return;
    }

    try {
      setLoading(true);
      setError('');
      await tournamentsApi.update(tournament.id, {
        teams_add: [selectedTeamId]
      });
      setShowAddModal(false);
      setSelectedTeamId('');
      onTeamsChange();
    } catch (err) {
      setError('Erro ao adicionar equipa');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveTeam = async (teamId: string, teamName: string) => {
    if (!window.confirm(`Remover "${teamName}" do torneio?`)) return;

    try {
      await tournamentsApi.update(tournament.id, {
        teams_remove: [teamId]
      });
      onTeamsChange();
    } catch (err) {
      console.error('Failed to remove team:', err);
      alert('Erro ao remover equipa');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Equipas Inscritas ({tournament.teams.length})
        </h2>
        <button
          onClick={() => {
            setShowAddModal(true);
            setError('');
            setSelectedTeamId('');
          }}
          className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
        >
          + Adicionar Equipa
        </button>
      </div>

      {tournament.teams.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhuma equipa inscrita</p>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {tournament.teams.map((team) => (
            <div
              key={team.id}
              className="flex justify-between items-center p-4 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
            >
              <div>
                <p className="font-medium text-gray-800">{team.name}</p>
                <p className="text-sm text-gray-600">{team.course.name}</p>
              </div>
              <button
                onClick={() => handleRemoveTeam(team.id, team.name)}
                className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded-md text-sm transition-colors"
              >
                Remover
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add Team Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Equipa</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">
                Equipa <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedTeamId}
                onChange={(e) => setSelectedTeamId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
              >
                <option value="">Selecione uma equipa</option>
                {availableTeams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name} - {team.course.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setShowAddModal(false)}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddTeam}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md disabled:opacity-50"
              >
                {loading ? 'A adicionar...' : 'Adicionar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Component to manage matches
const TournamentMatches = ({
  tournament,
  onMatchesChange
}: {
  tournament: TournamentDetail;
  onMatchesChange: () => void;
}) => {
  const navigate = useNavigate();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [teamHomeId, setTeamHomeId] = useState('');
  const [teamAwayId, setTeamAwayId] = useState('');
  const [location, setLocation] = useState('');
  const [startTime, setStartTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCreateMatch = async () => {
    if (!teamHomeId || !teamAwayId) {
      setError('Selecione as duas equipas');
      return;
    }

    if (teamHomeId === teamAwayId) {
      setError('As equipas devem ser diferentes');
      return;
    }

    if (!location.trim()) {
      setError('Local é obrigatório');
      return;
    }

    if (!startTime) {
      setError('Data e hora são obrigatórias');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const matchData: MatchCreate = {
        tournament_id: tournament.id,
        team_home_id: teamHomeId,
        team_away_id: teamAwayId,
        location: location.trim(),
        start_time: startTime
      };

      await matchesApi.create(matchData);
      setShowCreateModal(false);
      resetForm();
      onMatchesChange();
    } catch (err) {
      setError('Erro ao criar jogo');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setTeamHomeId('');
    setTeamAwayId('');
    setLocation('');
    setStartTime('');
    setError('');
  };

  const handleDeleteMatch = async (matchId: string) => {
    if (!window.confirm('Tem certeza que deseja eliminar este jogo?')) return;

    try {
      await matchesApi.delete(matchId);
      onMatchesChange();
    } catch (err) {
      console.error('Failed to delete match:', err);
      alert('Erro ao eliminar jogo');
    }
  };

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

  const getTeamName = (participants: Match['participants']): string => {
    const teamParticipant = participants.find(p => p.participant_type === 'team' && p.team);
    return teamParticipant?.team?.name || 'Equipa Desconhecida';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Jogos ({tournament.matches.length})
        </h2>
        <button
          onClick={() => {
            setShowCreateModal(true);
            resetForm();
          }}
          disabled={tournament.teams.length < 2}
          className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title={tournament.teams.length < 2 ? 'É necessário pelo menos 2 equipas' : ''}
        >
          + Criar Jogo
        </button>
      </div>

      {tournament.matches.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhum jogo criado</p>
      ) : (
        <div className="space-y-3">
          {tournament.matches.map((match) => (
            <div
              key={match.id}
              className="p-4 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-medium text-gray-800">
                      {getTeamName(match.participants.slice(0, 1))}
                    </span>
                    <span className="text-gray-500">vs</span>
                    <span className="font-medium text-gray-800">
                      {getTeamName(match.participants.slice(1, 2))}
                    </span>
                  </div>

                  {(match.home_score !== null || match.away_score !== null) && (
                    <div className="text-lg font-bold text-teal-600 mb-2">
                      {match.home_score ?? 0} - {match.away_score ?? 0}
                    </div>
                  )}

                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>📍 {match.location}</span>
                    <span>🕒 {new Date(match.start_time).toLocaleString('pt-PT')}</span>
                  </div>

                  <div className="mt-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}>
                      {getStatusText(match.status)}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/geral/jogos/${match.id}`)}
                    className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded-md text-sm transition-colors"
                  >
                    Ver
                  </button>
                  <button
                    onClick={() => handleDeleteMatch(match.id)}
                    className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded-md text-sm transition-colors"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Match Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Criar Jogo</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Equipa Casa <span className="text-red-500">*</span>
                </label>
                <select
                  value={teamHomeId}
                  onChange={(e) => setTeamHomeId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecione a equipa casa</option>
                  {tournament.teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Equipa Visitante <span className="text-red-500">*</span>
                </label>
                <select
                  value={teamAwayId}
                  onChange={(e) => setTeamAwayId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecione a equipa visitante</option>
                  {tournament.teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Local <span className="text-red-500">*</span>
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
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateMatch}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md disabled:opacity-50"
              >
                {loading ? 'A criar...' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main component
const TorneioDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [tournament, setTournament] = useState<TournamentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    loadTournament();
  }, [id]);

  const loadTournament = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const data = await tournamentsApi.getById(id);
      setTournament(data);
    } catch (err) {
      console.error('Failed to fetch tournament:', err);
      alert('Erro ao carregar torneio');
      navigate('/geral/torneios');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (data: TournamentUpdate) => {
    if (!id) return;

    const updated = await tournamentsApi.update(id, data);
    setTournament(updated);
  };

  const handleDelete = async () => {
    if (!id || !tournament) return;

    if (window.confirm(`Tem certeza que deseja eliminar "${tournament.name}"?`)) {
      try {
        await tournamentsApi.delete(id);
        navigate('/geral/torneios');
      } catch (err) {
        console.error('Failed to delete tournament:', err);
        alert('Erro ao eliminar torneio');
      }
    }
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

  if (!tournament) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Torneio</h1>
            <button
              onClick={() => navigate('/geral/torneios')}
              className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
            >
              Voltar
            </button>
          </div>

          {/* Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Tournament Info */}
            <div>
              <TournamentInfo
                tournament={tournament}
                onEdit={() => setShowEditModal(true)}
                onDelete={handleDelete}
              />
            </div>

            {/* Teams */}
            <div>
              <TournamentTeams
                tournament={tournament}
                onTeamsChange={loadTournament}
              />
            </div>
          </div>

          {/* Matches - Full Width */}
          <div className="mt-6">
            <TournamentMatches
              tournament={tournament}
              onMatchesChange={loadTournament}
            />
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <EditTournamentModal
          tournament={tournament}
          onClose={() => setShowEditModal(false)}
          onSave={handleUpdate}
        />
      )}
    </div>
  );
};

export default TorneioDetails;
