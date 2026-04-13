import { useState, useEffect, useMemo } from 'react';
import HelpTooltip from '../../components/HelpTooltip';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import ConfirmModal from '../../components/ConfirmModal';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentDetail, type TournamentUpdate, type TournamentCompetitor, type TournamentCompetitorDetail, type TournamentFinish } from '../../api/tournaments';
import { teamsApi, type Team } from '../../api/teams';
import { matchesApi, type Match, type MatchCreate, type ParticipantCreate } from '../../api/matches';
import { studentsApi, type Student } from '../../api/members';
import { btn } from '../../styles/buttonStyles';
import ListMatchesComponent from '../../components/matches/ListMatches';

// Component to display tournament information
const TournamentInfo = ({
  tournament,
  onEdit,
  onDelete,
  onActivate,
  onFinish
}: {
  tournament: TournamentDetail;
  onEdit: () => void;
  onDelete: () => void;
  onActivate: () => void;
  onFinish: () => void;
}) => {
  const [showScoringModal, setShowScoringModal] = useState(false);
  const [selectedEscalaoIdx, setSelectedEscalaoIdx] = useState(0);

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

  const scoringFormat = tournament.scoring_format;
  const escaloes = scoringFormat?.escaloes ?? [];
  const activeEscalao = escaloes[selectedEscalaoIdx];

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

      {scoringFormat && (
        <div>
          <label className="block text-teal-500 font-medium mb-2">Formato de Pontuação</label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-800">{scoringFormat.name}</span>
              {scoringFormat.is_playoff && (
                <span className="px-2 py-0.5 text-xs rounded-full bg-purple-100 text-purple-800 font-medium">
                  Playoff
                </span>
              )}
            </div>
            {escaloes.length > 0 && (
              <button
                onClick={() => { setSelectedEscalaoIdx(0); setShowScoringModal(true); }}
                className="text-sm text-teal-600 hover:text-teal-800 font-medium underline-offset-2 hover:underline transition-colors"
              >
                Ver detalhes
              </button>
            )}
          </div>
        </div>
      )}

      {showScoringModal && scoringFormat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowScoringModal(false)}>
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-gray-800">{scoringFormat.name}</h3>
                {scoringFormat.is_playoff && (
                  <span className="px-2 py-0.5 text-xs rounded-full bg-purple-100 text-purple-800 font-medium">
                    Playoff
                  </span>
                )}
              </div>
              <button onClick={() => setShowScoringModal(false)} className="text-gray-400 hover:text-gray-600 text-xl font-bold leading-none">✕</button>
            </div>

            {escaloes.length > 1 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {escaloes.map((esc, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedEscalaoIdx(idx)}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      idx === selectedEscalaoIdx
                        ? 'bg-teal-500 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {esc.escalao}
                  </button>
                ))}
              </div>
            )}

            {activeEscalao && (
              <div>
                {escaloes.length === 1 && (
                  <p className="text-sm font-semibold text-gray-700 mb-3">{activeEscalao.escalao}</p>
                )}
                {activeEscalao.minParticipants !== null || activeEscalao.maxParticipants !== null ? (
                  <p className="text-xs text-gray-500 mb-3">
                    Participantes:{' '}
                    {activeEscalao.minParticipants !== null ? `mín. ${activeEscalao.minParticipants}` : ''}
                    {activeEscalao.minParticipants !== null && activeEscalao.maxParticipants !== null ? ' — ' : ''}
                    {activeEscalao.maxParticipants !== null ? `máx. ${activeEscalao.maxParticipants}` : ''}
                  </p>
                ) : null}
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left px-4 py-2 text-gray-600 font-semibold border border-gray-200 w-20">Posição</th>
                      <th className="text-right px-4 py-2 text-gray-600 font-semibold border border-gray-200">Pontos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeEscalao.points.map((pts, i) => (
                      <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-2 border border-gray-200 text-gray-700 font-medium">{i + 1}º</td>
                        <td className="px-4 py-2 border border-gray-200 text-right text-teal-700 font-semibold">{pts}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex gap-4 pt-4">
        <button
          onClick={onEdit}
          className={`flex-1 px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors`}
        >
          Editar
        </button>
        <button
          onClick={onDelete}
          className={`flex-1 px-6 py-3 ${btn.danger} rounded-md font-medium transition-colors`}
        >
          Eliminar
        </button>
      </div>

      {tournament.status === 'draft' && (
        <div className="pt-4 border-t mt-4">
          <button
            onClick={onActivate}
            className={`w-full px-6 py-3 ${btn.success} rounded-md font-medium transition-colors`}
          >
            Ativar Torneio
          </button>
        </div>
      )}

      {tournament.status === 'active' && (
        <div className="pt-4 border-t mt-4">
          <button
            onClick={onFinish}
            className={`w-full px-6 py-3 ${btn.infoStrong} rounded-md font-medium transition-colors`}
          >
            Finalizar Torneio
          </button>
        </div>
      )}
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
  const [isPlayoff, setIsPlayoff] = useState(tournament.scoring_format?.is_playoff ?? false);
  const [saving, setSaving] = useState(false);
  const { notify } = useNotification();

  const handleSubmit = async () => {
    if (!name.trim()) {
      notify('Nome é obrigatório', 'error');
      return;
    }

    try {
      setSaving(true);
      await onSave({
        name: name.trim(),
        start_date: startDate || undefined,
        is_playoff: isPlayoff,
      });
      onClose();
    } catch (err) {
      notify('Não foi possível guardar as alterações ao torneio. Tente novamente.', 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Torneio</h2>

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
            <label className="block text-gray-700 font-medium mb-2">Data de Início <HelpTooltip text="Data em que o torneio começa oficialmente. Após esta data o torneio pode ser ativado e os jogos calendarizados." className="ml-1" /></label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_playoff_edit"
              checked={isPlayoff}
              onChange={(e) => setIsPlayoff(e.target.checked)}
              className="w-4 h-4 accent-teal-500"
            />
            <label htmlFor="is_playoff_edit" className="text-gray-700 font-medium cursor-pointer">
              Torneio de Playoff
            </label>
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={onClose}
            disabled={saving}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md disabled:opacity-50`}
          >
            {saving ? 'A guardar...' : 'Guardar'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Helper to get the display name of a tournament competitor
const getCompetitorName = (competitor: TournamentCompetitorDetail): string => {
  if (competitor.competitor_type === 'team' && competitor.team) {
    return competitor.team.name;
  }
  if (competitor.competitor_type === 'athlete' && competitor.athlete) {
    return competitor.athlete.full_name;
  }
  return 'Desconhecido';
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
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [selectedAthleteId, setSelectedAthleteId] = useState('');
  const [loading, setLoading] = useState(false);
  const [competitorToRemove, setCompetitorToRemove] = useState<{ competitor: TournamentCompetitorDetail; name: string } | null>(null);
  const [removingCompetitor, setRemovingCompetitor] = useState(false);
  const { notify } = useNotification();

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
    if (tournament.competitor_type === 'team' && !selectedTeamId) {
      notify('Selecione uma equipa', 'error');
      return;
    }
    if (tournament.competitor_type === 'athlete' && !selectedAthleteId) {
      notify('Selecione um atleta', 'error');
      return;
    }

    try {
      setLoading(true);

      const competitor: TournamentCompetitor = tournament.competitor_type === 'team'
        ? { competitor_type: 'team', team_id: selectedTeamId }
        : { competitor_type: 'athlete', athlete_id: selectedAthleteId };

      await tournamentsApi.addCompetitors(tournament.id, [competitor]);
      setShowAddModal(false);
      setSelectedTeamId('');
      setSelectedAthleteId('');
      onCompetitorsChange();
    } catch (err) {
      notify('Não foi possível adicionar o competidor. Poderá já estar inscrito neste torneio.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveCompetitor = (competitor: TournamentCompetitorDetail, name: string) => {
    setCompetitorToRemove({ competitor, name });
  };

  const confirmRemoveCompetitor = async () => {
    if (!competitorToRemove) return;

    try {
      setRemovingCompetitor(true);
      await tournamentsApi.removeCompetitors(tournament.id, [competitorToRemove.competitor.id]);
      setCompetitorToRemove(null);
      onCompetitorsChange();
    } catch (err) {
      console.error('Failed to remove competitor:', err);
      notify('Não foi possível remover o competidor do torneio. Tente novamente.', 'error');
    } finally {
      setRemovingCompetitor(false);
    }
  };

  const sortedCompetitors = useMemo(
    () => [...tournament.competitors].sort((a, b) => getCompetitorName(a).localeCompare(getCompetitorName(b))),
    [tournament.competitors]
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Competidores Inscritos ({tournament.competitors.length})
        </h2>
        <button
          onClick={() => {
            setShowAddModal(true);
            setSelectedTeamId('');
            setSelectedAthleteId('');
            setStudentSearchTerm('');
          }}
          className={`px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
        >
          + Adicionar Competidor
        </button>
      </div>

      {tournament.competitors.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Nenhum competidor inscrito</p>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {sortedCompetitors.map((competitor, idx) => {
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
                  className={`px-3 py-1 ${btn.dangerLight} rounded-md text-sm transition-colors`}
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

            <div className="space-y-4 mb-6">
              {tournament.competitor_type === 'team' ? (
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
                    {[...availableTeams].sort((a, b) => a.name.localeCompare(b.name)).map((team) => (
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
                      .sort((a, b) => a.full_name.localeCompare(b.full_name))
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
                className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
              >
                Cancelar
              </button>
              <button
                onClick={handleAddCompetitor}
                disabled={loading}
                className={`flex-1 px-4 py-2 ${btn.primary} rounded-md disabled:opacity-50`}
              >
                {loading ? 'A adicionar...' : 'Adicionar'}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={competitorToRemove !== null}
        title="Remover competidor"
        message={competitorToRemove ? `Remover "${competitorToRemove.name}" do torneio?` : ''}
        confirmLabel="Remover"
        variant="danger"
        loading={removingCompetitor}
        onCancel={() => {
          if (!removingCompetitor) {
            setCompetitorToRemove(null);
          }
        }}
        onConfirm={confirmRemoveCompetitor}
      />
    </div>
  );
};

// Component for finishing tournament with standings
const FinishTournamentModal = ({
  tournament,
  onClose,
  onFinish
}: {
  tournament: TournamentDetail;
  onClose: () => void;
  onFinish: (data: TournamentFinish) => Promise<void>;
}) => {
  const MAX_POSITIONS = 12; // Configurable number of positions
  const numPositions = Math.min(MAX_POSITIONS, tournament.competitors.length);

  // Map ranking position to competitor IDs (supports ties)
  const [positionAssignments, setPositionAssignments] = useState<Map<number, string[]>>(() => {
    const initial = new Map<number, string[]>();
    for (let position = 1; position <= numPositions; position += 1) {
      initial.set(position, ['']);
    }
    return initial;
  });
  const { notify } = useNotification();
  const [finishing, setFinishing] = useState(false);

  useEffect(() => {
    const initial = new Map<number, string[]>();
    for (let position = 1; position <= numPositions; position += 1) {
      initial.set(position, ['']);
    }
    setPositionAssignments(initial);
  }, [numPositions, tournament.id]);

  const getCompetitorId = (competitor: TournamentCompetitorDetail): string => {
    if (competitor.competitor_type === 'team' && competitor.team) {
      return competitor.team.id;
    }
    if (competitor.competitor_type === 'athlete' && competitor.athlete) {
      return competitor.athlete.id;
    }
    return '';
  };

  const sortedCompetitors = useMemo(
    () => [...tournament.competitors].sort((a, b) => getCompetitorName(a).localeCompare(getCompetitorName(b))),
    [tournament.competitors]
  );

  const getFilledCountAtPosition = (
    assignments: Map<number, string[]>,
    position: number
  ): number => {
    return (assignments.get(position) || []).filter(Boolean).length;
  };

  const getActivePositions = (assignments: Map<number, string[]> = positionAssignments): Set<number> => {
    const active = new Set<number>();
    let nextPosition = 1;

    while (nextPosition <= numPositions) {
      active.add(nextPosition);
      const filledCount = getFilledCountAtPosition(assignments, nextPosition);
      if (filledCount === 0) break;
      nextPosition += filledCount;
    }

    return active;
  };

  const normalizeAssignments = (assignments: Map<number, string[]>): Map<number, string[]> => {
    const active = getActivePositions(assignments);
    const normalized = new Map<number, string[]>();

    for (let position = 1; position <= numPositions; position += 1) {
      if (active.has(position)) {
        const existing = assignments.get(position) || [''];
        normalized.set(position, existing.length > 0 ? existing : ['']);
      } else {
        normalized.set(position, ['']);
      }
    }

    return normalized;
  };

  const handleCompetitorChange = (position: number, index: number, competitorId: string) => {
    const newAssignments = new Map(positionAssignments);
    const competitorsAtPosition = [...(newAssignments.get(position) || [])];
    competitorsAtPosition[index] = competitorId;
    newAssignments.set(position, competitorsAtPosition);
    setPositionAssignments(normalizeAssignments(newAssignments));
  };

  const addTieSlot = (position: number) => {
    const newAssignments = new Map(positionAssignments);
    const competitorsAtPosition = [...(newAssignments.get(position) || [])];
    competitorsAtPosition.push('');
    newAssignments.set(position, competitorsAtPosition);
    setPositionAssignments(normalizeAssignments(newAssignments));
  };

  const removeTieSlot = (position: number, index: number) => {
    const newAssignments = new Map(positionAssignments);
    const competitorsAtPosition = [...(newAssignments.get(position) || [])];

    if (competitorsAtPosition.length <= 1) {
      competitorsAtPosition[0] = '';
      newAssignments.set(position, competitorsAtPosition);
      setPositionAssignments(normalizeAssignments(newAssignments));
      return;
    }

    competitorsAtPosition.splice(index, 1);
    newAssignments.set(position, competitorsAtPosition);
    setPositionAssignments(normalizeAssignments(newAssignments));
  };

  const getAssignedCompetitorIds = (): string[] => {
    const assigned: string[] = [];
    positionAssignments.forEach((competitorsAtPosition) => {
      competitorsAtPosition.forEach((competitorId) => {
        if (competitorId) assigned.push(competitorId);
      });
    });
    return assigned;
  };

  const validateCompetitionRanking = (): string | null => {
    const activePositions = getActivePositions();

    for (let position = 1; position <= numPositions; position += 1) {
      const filledCount = getFilledCountAtPosition(positionAssignments, position);

      if (!activePositions.has(position) && filledCount > 0) {
        return `A posição ${position}º deve estar vazia devido a empates em posições anteriores`;
      }
    }

    let expectedPosition = 1;
    while (expectedPosition <= numPositions) {
      const filledCount = getFilledCountAtPosition(positionAssignments, expectedPosition);
      if (filledCount === 0) {
        return `A posição ${expectedPosition}º precisa de pelo menos um competidor`;
      }
      expectedPosition += filledCount;
    }

    return null;
  };

  const getPositionLabel = (position: number): string => {
    if (position === 1) return '1º Lugar';
    if (position === 2) return '2º Lugar';
    if (position === 3) return '3º Lugar';
    return `${position}º Lugar`;
  };

  const handleSubmit = async () => {
    const assignedCompetitorIds = getAssignedCompetitorIds();

    if (assignedCompetitorIds.length < numPositions) {
      notify(`Por favor, atribua ${numPositions} competidores no total`, 'error');
      return;
    }

    if (assignedCompetitorIds.length > numPositions) {
      notify(`Apenas ${numPositions} competidores podem ser classificados`, 'error');
      return;
    }

    const uniqueCompetitors = new Set(assignedCompetitorIds);
    if (uniqueCompetitors.size !== assignedCompetitorIds.length) {
      notify('Cada competidor só pode ser atribuído uma vez', 'error');
      return;
    }

    const rankingValidationError = validateCompetitionRanking();
    if (rankingValidationError) {
      notify(rankingValidationError, 'error');
      return;
    }

    try {
      setFinishing(true);

      // Build ranking entries
      const ranking_entries: (TournamentCompetitor & { competitor_id: string; position: number })[] = [];

      positionAssignments.forEach((competitorsAtPosition, position) => {
        competitorsAtPosition.forEach((competitorRecordId) => {
          if (!competitorRecordId) return;

          const competitor = tournament.competitors.find(c => c.id === competitorRecordId);

          if (competitor) {
            const entry: TournamentCompetitor & { competitor_id: string; position: number } = {
              competitor_id: competitor.id,
              competitor_type: competitor.competitor_type,
              position
            };

            const participantId = getCompetitorId(competitor);

            if (competitor.competitor_type === 'team') {
              entry.team_id = participantId;
            } else {
              entry.athlete_id = participantId;
            }

            ranking_entries.push(entry);
          }
        });
      });

      ranking_entries.sort((a, b) => a.position - b.position);

      await onFinish({ ranking_entries });
      onClose();
    } catch (err) {
      notify('Não foi possível finalizar o torneio. Certifique-se que todos os jogos foram concluídos.', 'error');
    } finally {
      setFinishing(false);
    }
  };

  const activePositions = getActivePositions();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Finalizar Torneio - Classificação Final</h2>

        <p className="text-gray-600 mb-6">
          Selecione os competidores por posição final. Para empates, adicione mais competidores na mesma posição.
        </p>

        <div className="space-y-3 mb-6">
          {Array.from({ length: numPositions }, (_, i) => i + 1)
            .filter((position) => activePositions.has(position))
            .map((position) => {
            const competitorsAtPosition = positionAssignments.get(position) || [''];

            return (
              <div
                key={position}
                className="p-4 bg-gray-50 rounded-md"
              >
                <div className="flex justify-between items-center mb-2">
                  <label className="text-gray-800 font-semibold">{getPositionLabel(position)}</label>
                  <button
                    type="button"
                    onClick={() => addTieSlot(position)}
                    className="text-sm px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors"
                  >
                    + Empate
                  </button>
                </div>

                <div className="space-y-2">
                  {competitorsAtPosition.map((competitorRecordId, index) => {
                    const selectedElsewhere = new Set(
                      getAssignedCompetitorIds().filter((id, idx, arr) => {
                        if (id !== competitorRecordId) return true;
                        const first = arr.indexOf(id);
                        return first !== idx;
                      })
                    );

                    return (
                      <div key={`${position}-${index}`} className="flex gap-2">
                        <select
                          value={competitorRecordId}
                          onChange={(e) => handleCompetitorChange(position, index, e.target.value)}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Selecione um competidor...</option>
                          {sortedCompetitors.map((competitor) => {
                            const competitorRecordIdOption = competitor.id;
                            const participantName = getCompetitorName(competitor);
                            const isDisabled = selectedElsewhere.has(competitorRecordIdOption) && competitorRecordIdOption !== competitorRecordId;

                            return (
                              <option
                                key={competitorRecordIdOption}
                                value={competitorRecordIdOption}
                                disabled={isDisabled}
                              >
                                {participantName} ({competitor.competitor_type === 'team' ? 'Equipa' : 'Atleta'})
                                {isDisabled ? ' - Já atribuído' : ''}
                              </option>
                            );
                          })}
                        </select>

                        {competitorsAtPosition.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeTieSlot(position, index)}
                            className="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors"
                            title="Remover empate"
                          >
                            ✕
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {numPositions < tournament.competitors.length && (
          <div className="mb-4 p-3 bg-yellow-100 border border-yellow-400 text-yellow-800 rounded-md text-sm">
            Nota: Apenas os primeiros {numPositions} lugares serão registados. {tournament.competitors.length - numPositions} competidor(es) não terão posição atribuída.
          </div>
        )}

        <div className="flex gap-4">
          <button
            onClick={onClose}
            disabled={finishing}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={finishing}
            className={`flex-1 px-4 py-2 ${btn.infoStrong} rounded-md disabled:opacity-50`}
          >
            {finishing ? 'A finalizar...' : 'Finalizar Torneio'}
          </button>
        </div>
      </div>
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
  const [matchToDelete, setMatchToDelete] = useState<string | null>(null);
  const [deletingMatch, setDeletingMatch] = useState(false);
  const { notify } = useNotification();
  const [matchStatusFilter, setMatchStatusFilter] = useState<string>('all');

  const handleCreateMatch = async () => {
    // Validate at least 2 participants
    const validParticipants = selectedParticipants.filter(p => p.trim() !== '');
    if (validParticipants.length < 2) {
      notify('Selecione pelo menos 2 participantes', 'error');
      return;
    }

    // Check for duplicates
    const uniqueParticipants = new Set(validParticipants);
    if (uniqueParticipants.size !== validParticipants.length) {
      notify('Os participantes devem ser diferentes', 'error');
      return;
    }

    if (!location.trim()) {
      notify('Local é obrigatório', 'error');
      return;
    }

    if (!startTime) {
      notify('Data e hora são obrigatórias', 'error');
      return;
    }

    try {
      setLoading(true);

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
      notify('Não foi possível criar o jogo. Verifique os dados e tente novamente.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedParticipants(['', '']);
    setLocation('');
    setStartTime('');
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

  const handleDeleteMatch = (matchId: string) => {
    setMatchToDelete(matchId);
  };

  const confirmDeleteMatch = async () => {
    if (!matchToDelete) return;

    try {
      setDeletingMatch(true);
      await matchesApi.delete(matchToDelete);
      onMatchDeleted(matchToDelete);
      setMatchToDelete(null);
    } catch (err) {
      console.error('Failed to delete match:', err);
      notify('Não foi possível eliminar o jogo. Poderá ter resultados ou convocatórias registadas.', 'error');
    } finally {
      setDeletingMatch(false);
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
            className={`px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
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
                    type="button"
                    onClick={() => handleDeleteMatch(match.id)}
                    className={`px-3 py-1 ${btn.dangerLight} rounded-md text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-red-400`}
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Criar Jogo</h2>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-gray-700 font-medium">
                    Participantes <HelpTooltip text="Selecione os competidores que vão disputar este jogo. São necessários no mínimo 2 participantes. Só podem ser selecionados competidores já inscritos no torneio." className="ml-1" /> <span className="text-red-500">*</span>
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
                  Local <HelpTooltip text="Local onde o jogo vai decorrer, ex: Campo Municipal, Pavilhão Principal. Esta informação é visível aos participantes." className="ml-1" /> <span className="text-red-500">*</span>
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
                {loading ? 'A criar...' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal
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
      />
    </div>
  );
};

// Main component
const TorneioDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [tournament, setTournament] = useState<TournamentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showFinishModal, setShowFinishModal] = useState(false);
  const [activating, setActivating] = useState(false);
  const [showActivateModal, setShowActivateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingTournament, setDeletingTournament] = useState(false);
  const { notify } = useNotification();

  // Determine where to navigate back to
  const fromModalityId = searchParams.get('fromModality');
  const handleBack = () => {
    if (fromModalityId) {
      navigate(`/geral/modalidades/${fromModalityId}`);
    } else {
      navigate('/geral/torneios');
    }
  };

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
      notify('Não foi possível carregar os dados do torneio. Tente recarregar a página.', 'error');
      handleBack();
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (data: TournamentUpdate) => {
    if (!id) return;

    const updated = await tournamentsApi.update(id, data);
    setTournament(updated);
    notify('Torneio atualizado com sucesso', 'success');
  };

  const handleActivate = () => {
    if (!id || !tournament) return;

    setShowActivateModal(true);
  };

  const confirmActivate = async () => {
    if (!id || !tournament) return;

    try {
      setActivating(true);
      const updated = await tournamentsApi.update(id, { status: 'active' });
      setTournament(updated);
      setShowActivateModal(false);
    } catch (err) {
      console.error('Failed to activate tournament:', err);
      notify('Não foi possível ativar o torneio. Verifique se estão reunidas as condições necessárias.', 'error');
    } finally {
      setActivating(false);
    }
  };

  const handleDelete = () => {
    if (!id || !tournament) return;

    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!id || !tournament) return;

    try {
      setDeletingTournament(true);
      await tournamentsApi.delete(id);
      handleBack();
    } catch (err) {
      console.error('Failed to delete tournament:', err);
      notify('Não foi possível eliminar o torneio. Poderá ter jogos ou competidores associados.', 'error');
    } finally {
      setDeletingTournament(false);
    }
  };

  const handleFinish = async (data: TournamentFinish) => {
    if (!id) return;

    const updated = await tournamentsApi.finish(id, data);
    setTournament(updated);
    notify('Torneio finalizado com sucesso', 'success');
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
              onClick={handleBack}
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
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
                onActivate={handleActivate}
                onFinish={() => setShowFinishModal(true)}
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
            <ListMatchesComponent tournamentId={tournament.id} />
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

      {showFinishModal && (
        <FinishTournamentModal
          tournament={tournament}
          onClose={() => setShowFinishModal(false)}
          onFinish={handleFinish}
        />
      )}

      <ConfirmModal
        isOpen={showActivateModal}
        title="Ativar torneio"
        message={tournament ? `Ativar o torneio "${tournament.name}"? O torneio passará a estar ativo e visível.` : ''}
        confirmLabel="Ativar"
        variant="success"
        loading={activating}
        onCancel={() => {
          if (!activating) {
            setShowActivateModal(false);
          }
        }}
        onConfirm={confirmActivate}
      />

      <ConfirmModal
        isOpen={showDeleteModal}
        title="Eliminar torneio"
        message={tournament ? `Tem certeza que deseja eliminar "${tournament.name}"?` : ''}
        confirmLabel="Eliminar"
        variant="danger"
        loading={deletingTournament}
        onCancel={() => {
          if (!deletingTournament) {
            setShowDeleteModal(false);
          }
        }}
        onConfirm={confirmDelete}
      />
    </div>
  );
};

export default TorneioDetails;
