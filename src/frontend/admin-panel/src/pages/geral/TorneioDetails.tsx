import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { tournamentsApi, type TournamentDetail, type TournamentUpdate, type TournamentCompetitor, type TournamentCompetitorDetail } from '../../api/tournaments';
import { teamsApi, type Team } from '../../api/teams';
import { matchesApi, type Match, type MatchCreate, type ParticipantCreate } from '../../api/matches';
import { studentsApi, type Student } from '../../api/members';

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

// Component to manage competitors in tournament
const TournamentCompetitors = ({
  tournament,
  onCompetitorsChange
}: {
  tournament: TournamentDetail;
  onCompetitorsChange: () => void;
}) => {
  const [availableTeams, setAvailableTeams] = useState<Team[]>([]);
  const [availableStudents, setAvailableStudents] = useState<Student[]>([]);
  const [studentSearchTerm, setStudentSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedCompetitorType, setSelectedCompetitorType] = useState<'team' | 'athlete'>('team');
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [selectedAthleteId, setSelectedAthleteId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAvailableTeams();
    loadAvailableStudents();
  }, [tournament]);

  const loadAvailableTeams = async () => {
    try {
      const allTeams = await teamsApi.getAll({ modality_id: tournament.modality.id });
      // Filter out teams already in tournament
      const teamIds = new Set(
        tournament.competitors
          .filter(c => c.competitor_type === 'team' && c.team)
          .map(c => c.team.id)
      );
      setAvailableTeams(allTeams.filter(t => !teamIds.has(t.id)));
    } catch (err) {
      console.error('Failed to load teams:', err);
    }
  };

  const loadAvailableStudents = async () => {
    try {
      const allStudents = await studentsApi.getAll();
      // Filter out students already in tournament and only show members
      const athleteIds = new Set(
        tournament.competitors
          .filter(c => c.competitor_type === 'athlete' && c.athlete)
          .map(c => c.athlete.id)
      );
      setAvailableStudents(
        allStudents.filter(s => s.is_member && !athleteIds.has(s.id))
      );
    } catch (err) {
      console.error('Failed to load students:', err);
    }
  };

  const handleAddCompetitor = async () => {
    if (selectedCompetitorType === 'team' && !selectedTeamId) {
      setError('Selecione uma equipa');
      return;
    }
    if (selectedCompetitorType === 'athlete' && !selectedAthleteId) {
      setError('Selecione um atleta');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const competitor: TournamentCompetitor = selectedCompetitorType === 'team'
        ? { competitor_type: 'team', team_id: selectedTeamId }
        : { competitor_type: 'athlete', athlete_id: selectedAthleteId };

      await tournamentsApi.addCompetitors(tournament.id, [competitor]);
      setShowAddModal(false);
      setSelectedTeamId('');
      setSelectedAthleteId('');
      onCompetitorsChange();
    } catch (err) {
      setError('Erro ao adicionar competidor');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveCompetitor = async (competitor: TournamentCompetitorDetail, name: string) => {
    if (!window.confirm(`Remover "${name}" do torneio?`)) return;

    try {
      await tournamentsApi.removeCompetitors(tournament.id, [competitor.id]);
      onCompetitorsChange();
    } catch (err) {
      console.error('Failed to remove competitor:', err);
      alert('Erro ao remover competidor');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Competidores Inscritos ({tournament.competitors.length})
        </h2>
        <button
          onClick={() => {
            setShowAddModal(true);
            setError('');
            setSelectedTeamId('');
            setSelectedAthleteId('');
            setStudentSearchTerm('');
            setSelectedCompetitorType('team');
          }}
          className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
        >
          + Adicionar Competidor
        </button>
      </div>

      {tournament.competitors.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhum competidor inscrito</p>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {tournament.competitors.map((competitor, idx) => {
            const isTeam = competitor.competitor_type === 'team';
            const name = isTeam ? competitor.team?.name : competitor.athlete?.full_name;
            const subtitle = isTeam ? competitor.team?.course?.name : competitor.athlete?.course?.name;

            return (
              <div
                key={`${competitor.competitor_type}-${isTeam ? competitor.team?.id : competitor.athlete?.id}-${idx}`}
                className="flex justify-between items-center p-4 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-gray-800">{name}</p>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800">
                      {isTeam ? 'Equipa' : 'Atleta'}
                    </span>
                  </div>
                  {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
                </div>
                <button
                  onClick={() => handleRemoveCompetitor(competitor, name || 'Desconhecido')}
                  className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded-md text-sm transition-colors"
                >
                  Remover
                </button>
              </div>
            );
          })}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Competidor</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedCompetitorType}
                  onChange={(e) => setSelectedCompetitorType(e.target.value as 'team' | 'athlete')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                >
                  <option value="team">Equipa</option>
                  <option value="athlete">Atleta</option>
                </select>
              </div>

              {selectedCompetitorType === 'team' ? (
                <div>
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
              ) : (
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Atleta <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={studentSearchTerm}
                    onChange={(e) => setStudentSearchTerm(e.target.value)}
                    placeholder="Pesquisar por nome ou número..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 mb-2"
                  />
                  <select
                    value={selectedAthleteId}
                    onChange={(e) => setSelectedAthleteId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                    size={Math.min(availableStudents.filter(s =>
                      studentSearchTerm === '' ||
                      s.full_name.toLowerCase().includes(studentSearchTerm.toLowerCase()) ||
                      s.student_number.includes(studentSearchTerm)
                    ).length + 1, 8)}
                  >
                    <option value="">Selecione um atleta</option>
                    {availableStudents
                      .filter(s =>
                        studentSearchTerm === '' ||
                        s.full_name.toLowerCase().includes(studentSearchTerm.toLowerCase()) ||
                        s.student_number.includes(studentSearchTerm)
                      )
                      .map((student) => (
                        <option key={student.id} value={student.id}>
                          {student.full_name} ({student.student_number}) - {student.course.name}
                        </option>
                      ))}
                  </select>
                  {availableStudents.length === 0 && (
                    <p className="mt-1 text-sm text-gray-500">Nenhum atleta disponível</p>
                  )}
                </div>
              )}
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
                onClick={handleAddCompetitor}
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
  onMatchesChange,
  onMatchDeleted
}: {
  tournament: TournamentDetail;
  onMatchesChange: () => void;
  onMatchDeleted: (matchId: string) => void;
}) => {
  const navigate = useNavigate();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>(['', '']);
  const [location, setLocation] = useState('');
  const [startTime, setStartTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [matchStatusFilter, setMatchStatusFilter] = useState<string>('all');

  const handleCreateMatch = async () => {
    // Validate at least 2 participants
    const validParticipants = selectedParticipants.filter(p => p.trim() !== '');
    if (validParticipants.length < 2) {
      setError('Selecione pelo menos 2 participantes');
      return;
    }

    // Check for duplicates
    const uniqueParticipants = new Set(validParticipants);
    if (uniqueParticipants.size !== validParticipants.length) {
      setError('Os participantes devem ser diferentes');
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

      // Map selected IDs to ParticipantCreate objects, detecting the type from tournament.competitors
      const participants: ParticipantCreate[] = validParticipants.map(competitorId => {
        const competitor = tournament.competitors.find(c =>
          (c.competitor_type === 'team' && c.team?.id === competitorId) ||
          (c.competitor_type === 'athlete' && c.athlete?.id === competitorId)
        );

        if (competitor?.competitor_type === 'athlete') {
          return {
            participant_type: 'athlete',
            athlete_id: competitorId
          };
        } else {
          return {
            participant_type: 'team',
            team_id: competitorId
          };
        }
      });

      const matchData: MatchCreate = {
        tournament_id: tournament.id,
        location: location.trim(),
        start_time: startTime,
        participants
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
    setSelectedParticipants(['', '']);
    setLocation('');
    setStartTime('');
    setError('');
  };

  const addParticipantSlot = () => {
    setSelectedParticipants([...selectedParticipants, '']);
  };

  const removeParticipantSlot = (index: number) => {
    if (selectedParticipants.length > 2) {
      setSelectedParticipants(selectedParticipants.filter((_, i) => i !== index));
    }
  };

  const updateParticipant = (index: number, value: string) => {
    const updated = [...selectedParticipants];
    updated[index] = value;
    setSelectedParticipants(updated);
  };

  const handleDeleteMatch = async (matchId: string) => {
    if (!window.confirm('Tem certeza que deseja eliminar este jogo?')) return;

    try {
      await matchesApi.delete(matchId);
      onMatchDeleted(matchId);
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

  const getParticipantNames = (participants: Match['participants']): string => {
    const names = participants.map(p => {
      if (p.participant_type === 'team' && p.team) {
        return p.team.name;
      } else if (p.participant_type === 'athlete' && p.athlete) {
        return p.athlete.full_name;
      }
      return 'Desconhecido';
    });
    return names.join(' vs ');
  };

  const getParticipantScores = (participants: Match['participants']): string | null => {
    if (participants.every(p => p.score !== null && p.score !== undefined)) {
      return participants.map(p => p.score).join(' - ');
    }
    return null;
  };

  const filteredMatches = tournament.matches.filter(match =>
    matchStatusFilter === 'all' || match.status === matchStatusFilter
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Jogos ({tournament.matches.length})
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
          <button
            onClick={() => {
              setShowCreateModal(true);
              resetForm();
            }}
            disabled={tournament.competitors.length < 2}
            className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={tournament.competitors.length < 2 ? 'É necessário pelo menos 2 competidores' : ''}
          >
            + Criar Jogo
          </button>
        </div>
      </div>

      {tournament.matches.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhum jogo criado</p>
      ) : filteredMatches.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhum jogo com o estado selecionado</p>
      ) : (
        <div className="space-y-3">
          {filteredMatches.map((match) => (
            <div
              key={match.id}
              onClick={() => navigate(`/geral/jogos/${match.id}`)}
              className="p-4 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
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
                    <span>{new Date(match.start_time).toLocaleString('pt-PT', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</span>
                  </div>

                  <div className="mt-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}>
                      {getStatusText(match.status)}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
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
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-gray-700 font-medium">
                    Participantes <span className="text-red-500">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={addParticipantSlot}
                    className="text-sm px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors"
                  >
                    + Adicionar Participante
                  </button>
                </div>
                <div className="space-y-2">
                  {selectedParticipants.map((participantId, index) => (
                    <div key={index} className="flex gap-2">
                      <select
                        value={participantId}
                        onChange={(e) => updateParticipant(index, e.target.value)}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                      >
                        <option value="">Selecione um participante</option>
                        {tournament.competitors.map((competitor) => {
                          const isTeam = competitor.competitor_type === 'team';
                          const id = isTeam ? competitor.team?.id : competitor.athlete?.id;
                          const name = isTeam ? competitor.team?.name : competitor.athlete?.full_name;
                          const label = isTeam ? name : `${name} (Atleta)`;

                          return (
                            <option key={`${competitor.competitor_type}-${id}`} value={id}>
                              {label}
                            </option>
                          );
                        })}
                      </select>
                      {selectedParticipants.length > 2 && (
                        <button
                          type="button"
                          onClick={() => removeParticipantSlot(index)}
                          className="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors"
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
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!tournament) return null;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Torneio</h1>
            <button
              onClick={() => navigate('/geral/torneios')}
              className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
            >
              Voltar
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <TournamentInfo
                tournament={tournament}
                onEdit={() => setShowEditModal(true)}
                onDelete={handleDelete}
              />
            </div>

            <div>
              <TournamentCompetitors
                tournament={tournament}
                onCompetitorsChange={loadTournament}
              />
            </div>
          </div>

          <div className="mt-6">
            <TournamentMatches
              tournament={tournament}
              onMatchesChange={loadTournament}
              onMatchDeleted={(matchId) => setTournament(prev => prev ? { ...prev, matches: prev.matches.filter(m => m.id !== matchId) } : null)}
            />
          </div>
        </div>
      </div>

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
