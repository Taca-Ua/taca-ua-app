import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { tournamentsApi, type Tournament } from '../../api/tournaments';
import { teamsApi, type Team } from '../../api/teams';
import { matchesApi, type Match, type MatchCreate } from '../../api/matches';
import { coursesApi, type Course } from '../../api/courses';

const TorneioDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [isEditModal, setIsEditModal] = useState(false);
  const [isAddTeamModal, setIsAddTeamModal] = useState(false);
  const [isAddMatchModal, setIsAddMatchModal] = useState(false);

  // Campos edição
  const [editName, setEditName] = useState('');
  const [editRules, setEditRules] = useState('');
  const [editStartDate, setEditStartDate] = useState('');

  // Novo team
  const [selectedTeamId, setSelectedTeamId] = useState('');

  // Novo match
  const [matchTeamHome, setMatchTeamHome] = useState('');
  const [matchTeamAway, setMatchTeamAway] = useState('');
  const [matchLocation, setMatchLocation] = useState('');
  const [matchStartTime, setMatchStartTime] = useState('');

  const fetchData = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const [tournamentData, teamsData, matchesData, coursesData] = await Promise.all([
        tournamentsApi.getById(Number(id)),
        teamsApi.getAll(true), // Get all teams
        matchesApi.getAll(), // Get all matches
        coursesApi.getAll(), // Get all courses/nucleos
      ]);
      setTournament(tournamentData);
      setTeams(teamsData);
      setCourses(coursesData);
      // Filter matches for this tournament
      const tournamentMatches = matchesData.filter(m => m.tournament_id === Number(id));
      setMatches(tournamentMatches);
      setError('');
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const openEdit = () => {
    if (!tournament) return;
    setEditName(tournament.name);
    setEditRules(tournament.rules ?? '');
    setEditStartDate(tournament.start_date ?? '');
    setIsEditModal(true);
  };

  const saveEdit = async () => {
    if (!tournament) return;

    try {
      const updated = await tournamentsApi.update(tournament.id, {
        name: editName,
        rules: editRules || undefined,
        start_date: editStartDate || undefined,
      });
      setTournament(updated);
      setIsEditModal(false);
      setError('');
    } catch (err) {
      console.error('Failed to update tournament:', err);
      setError('Erro ao atualizar torneio');
    }
  };

  const deleteTournament = async () => {
    if (!tournament) return;
    if (!window.confirm("Tem certeza que deseja eliminar este torneio?")) return;

    try {
      await tournamentsApi.delete(tournament.id);
      navigate('/geral/torneios');
    } catch (err) {
      console.error('Failed to delete tournament:', err);
      setError('Erro ao eliminar torneio');
    }
  };

  const activateTournament = async () => {
    if (!tournament) return;
    if (!window.confirm("Ativar torneio? Isso permitirá que jogos sejam jogados.")) return;

    try {
      const updated = await tournamentsApi.update(tournament.id, {
        status: 'active',
      });
      setTournament(updated);
      setError('');
    } catch (err) {
      console.error('Failed to activate tournament:', err);
      setError('Erro ao ativar torneio');
    }
  };

  const finishTournament = async () => {
    if (!tournament) return;
    if (!window.confirm("Finalizar torneio? Isso bloqueará edições.")) return;

    try {
      const finished = await tournamentsApi.finish(tournament.id);
      setTournament(finished);
      setError('');
    } catch (err) {
      console.error('Failed to finish tournament:', err);
      setError('Erro ao finalizar torneio');
    }
  };

  const addTeam = async () => {
    if (!tournament || !selectedTeamId) return;

    const teamId = Number(selectedTeamId);

    // Check if team is already added
    if (tournament.teams?.includes(teamId)) {
      alert('Esta equipa já foi adicionada ao torneio.');
      return;
    }

    try {
      const updatedTeams = [...(tournament.teams || []), teamId];
      const updated = await tournamentsApi.update(tournament.id, {
        teams: updatedTeams,
      });
      setTournament(updated);
      setSelectedTeamId('');
      setIsAddTeamModal(false);
      setError('');
    } catch (err) {
      console.error('Failed to add team:', err);
      setError('Erro ao adicionar equipa');
    }
  };

  const getTeamName = (teamId: number) => {
    const team = teams.find(t => t.id === teamId);
    if (!team) return `Equipa ${teamId}`;

    const course = courses.find(c => c.id === team.course_id);
    const courseName = course ? course.abbreviation : `Curso ${team.course_id}`;

    return `${team.name} (${courseName})`;
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      scheduled: 'Agendado',
      in_progress: 'Em Curso',
      finished: 'Terminado',
      cancelled: 'Cancelado',
    };
    return labels[status] || status;
  };

  const handleCreateMatch = async () => {
    if (!tournament || !matchTeamHome || !matchTeamAway || !matchLocation || !matchStartTime) {
      alert('Todos os campos são obrigatórios');
      return;
    }

    if (matchTeamHome === matchTeamAway) {
      alert('As equipas devem ser diferentes');
      return;
    }

    try {
      const newMatchData: MatchCreate = {
        tournament_id: tournament.id,
        team_home_id: Number(matchTeamHome),
        team_away_id: Number(matchTeamAway),
        location: matchLocation,
        start_time: matchStartTime,
      };

      const newMatch = await matchesApi.create(newMatchData);
      setMatches([...matches, newMatch]);

      // Reset form
      setMatchTeamHome('');
      setMatchTeamAway('');
      setMatchLocation('');
      setMatchStartTime('');
      setIsAddMatchModal(false);
      setError('');
    } catch (err) {
      console.error('Failed to create match:', err);
      setError('Erro ao criar jogo');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="p-10 text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
          <p className="mt-2 text-gray-600">A carregar...</p>
        </div>
      </div>
    );
  }

  if (!tournament) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="p-10 text-center text-red-600">Torneio não encontrado.</div>
      </div>
    );
  }

  const isLocked = tournament.status === 'finished';

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex justify-between mb-8 items-center">
          <h1 className="text-3xl font-bold text-gray-800">Gestão do Torneio</h1>

          <div className="flex gap-3">

            {/* Ativar - only if status is 'draft' */}
            {tournament.status === 'draft' && (
              <button
                onClick={activateTournament}
                className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md"
              >
                Ativar Torneio
              </button>
            )}

            {/* Finalizar - only if status is 'active' */}
            {tournament.status === 'active' && (
              <button
                onClick={finishTournament}
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-md"
              >
                Finalizar Torneio
              </button>
            )}

            {/* Eliminar */}
            <button
              onClick={deleteTournament}
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-md"
            >
              Eliminar
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {/* Draft Warning */}
        {tournament.status === 'draft' && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-300 text-yellow-800 rounded-md">
            <strong>⚠️ Torneio em Rascunho:</strong> Este torneio está em modo de rascunho.
            Ative o torneio para permitir a criação de jogos.
          </div>
        )}

        {/* Finished Info */}
        {isLocked && (
          <div className="mb-6 p-4 bg-gray-100 border border-gray-300 text-gray-700 rounded-md">
            <strong>🔒 Torneio Finalizado:</strong> Este torneio foi finalizado e não pode ser editado.
          </div>
        )}

        {/* GRID */}
        <div className="grid grid-cols-3 gap-8">

          {/* COL 1 - Detalhes */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Detalhes</h2>

            <div className="space-y-4">

              <div>
                <label className="font-medium text-teal-600">Nome</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.name}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Modalidade ID</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.modality_id}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Época</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.season_year || 'N/A'}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Estado</label>
                <div className="bg-gray-100 p-3 rounded-md capitalize">{tournament.status}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Regras</label>
                <pre className="bg-gray-100 p-3 rounded-md whitespace-pre-wrap">
                  {tournament.rules ?? "Nenhuma"}
                </pre>
              </div>

              <div>
                <label className="font-medium text-teal-600">Data de início</label>
                <div className="bg-gray-100 p-3 rounded-md">
                  {tournament.start_date ?? "Não definida"}
                </div>
              </div>

              {!isLocked && (
                <div className="pt-4">
                  <button
                    onClick={openEdit}
                    className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md"
                  >
                    Editar
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* COL 2 - Equipas */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Equipas</h2>

            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {tournament.teams && tournament.teams.length > 0 ? (
                tournament.teams.map((teamId) => (
                  <div
                    key={teamId}
                    className="bg-gray-100 px-4 py-2 rounded-md text-gray-700"
                  >
                    {getTeamName(teamId)}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 italic">Nenhuma equipa adicionada</p>
              )}
            </div>

            {!isLocked && (
              <div className="pt-4">
                <button
                  onClick={() => setIsAddTeamModal(true)}
                  className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md"
                >
                  + Adicionar Equipa
                </button>
              </div>
            )}
          </div>

          {/* COL 3 - Jogos */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Jogos</h2>

            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {matches.length > 0 ? (
                matches.map(match => (
                  <div
                    key={match.id}
                    onClick={() => navigate(`/geral/jogos/${match.id}`)}
                    className="bg-gray-100 px-4 py-3 rounded-md hover:bg-gray-200 cursor-pointer"
                  >
                    <div className="flex justify-between items-center">
                      <div className="text-sm font-medium">
                        {getTeamName(match.team_home_id)} vs {getTeamName(match.team_away_id)}
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${
                        match.status === 'finished' ? 'bg-green-100 text-green-700' :
                        match.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
                        match.status === 'cancelled' ? 'bg-red-100 text-red-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {getStatusLabel(match.status)}
                      </span>
                    </div>
                    {match.status === 'finished' && match.home_score !== null && match.away_score !== null && (
                      <div className="text-xs text-gray-600 mt-1">
                        Resultado: {match.home_score} - {match.away_score}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 italic">Nenhum jogo criado</p>
              )}
            </div>

            {!isLocked && (
              <div className="pt-4">
                {tournament.status === 'draft' ? (
                  <div>
                    <button
                      disabled
                      className="w-full bg-gray-300 text-gray-500 py-2 rounded-md cursor-not-allowed"
                      title="Ative o torneio para criar jogos"
                    >
                      + Novo Jogo
                    </button>
                    <p className="text-xs text-gray-500 mt-2 text-center">
                      Ative o torneio primeiro
                    </p>
                  </div>
                ) : (
                  <button
                    onClick={() => setIsAddMatchModal(true)}
                    className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md"
                  >
                    + Novo Jogo
                  </button>
                )}
              </div>
            )}
          </div>

        </div>
      </div>

      {/* ==================== MODAL EDITAR ==================== */}
      {isEditModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">

            <h2 className="text-2xl font-bold mb-6">Editar Torneio</h2>

            <div className="space-y-4">
              <div>
                <label className="font-medium">Nome</label>
                <input
                  className="border w-full px-4 py-2 rounded-md"
                  value={editName}
                  onChange={e => setEditName(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Regras (JSON)</label>
                <textarea
                  className="border w-full px-4 py-2 rounded-md min-h-[80px]"
                  value={editRules}
                  onChange={e => setEditRules(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Data de início</label>
                <input
                  type="date"
                  className="border w-full px-4 py-2 rounded-md"
                  value={editStartDate}
                  onChange={e => setEditStartDate(e.target.value)}
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsEditModal(false)}
                className="flex-1 bg-gray-300 py-2 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={saveEdit}
                className="flex-1 bg-teal-500 text-white py-2 rounded-md"
              >
                Guardar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ==================== MODAL ADD TEAM ==================== */}
      {!isLocked && isAddTeamModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">

            <h2 className="text-2xl font-bold mb-6">Adicionar Equipa</h2>

            <div>
              <label className="block font-medium mb-2">Selecionar Equipa</label>
              <select
                className="border w-full px-4 py-2 rounded-md bg-white"
                value={selectedTeamId}
                onChange={e => setSelectedTeamId(e.target.value)}
              >
                <option value="">Selecionar equipa...</option>
                {teams
                  .filter(team => !tournament?.teams?.includes(team.id))
                  .map(team => {
                    const course = courses.find(c => c.id === team.course_id);
                    const courseName = course ? course.abbreviation : `Curso ${team.course_id}`;
                    return (
                      <option key={team.id} value={team.id}>
                        {team.name} ({courseName})
                      </option>
                    );
                  })}
              </select>
              {teams.filter(team => !tournament?.teams?.includes(team.id)).length === 0 && (
                <p className="text-sm text-gray-500 mt-2 italic">Todas as equipas já foram adicionadas</p>
              )}
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsAddTeamModal(false);
                  setSelectedTeamId('');
                }}
                className="flex-1 bg-gray-300 hover:bg-gray-400 py-2 rounded-md transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={addTeam}
                disabled={!selectedTeamId}
                className="flex-1 bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Adicionar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ==================== MODAL ADD MATCH ==================== */}
      {!isLocked && isAddMatchModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">

            <h2 className="text-2xl font-bold mb-6">Criar Novo Jogo</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              {/* Team Home */}
              <div>
                <label className="block font-medium mb-2">Equipa Casa <span className="text-red-500">*</span></label>
                <select
                  className="border w-full px-4 py-2 rounded-md bg-white"
                  value={matchTeamHome}
                  onChange={e => setMatchTeamHome(e.target.value)}
                >
                  <option value="">Selecionar equipa...</option>
                  {tournament?.teams?.map(teamId => (
                    <option key={teamId} value={teamId}>
                      {getTeamName(teamId)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Team Away */}
              <div>
                <label className="block font-medium mb-2">Equipa Visitante <span className="text-red-500">*</span></label>
                <select
                  className="border w-full px-4 py-2 rounded-md bg-white"
                  value={matchTeamAway}
                  onChange={e => setMatchTeamAway(e.target.value)}
                >
                  <option value="">Selecionar equipa...</option>
                  {tournament?.teams?.map(teamId => (
                    <option key={teamId} value={teamId}>
                      {getTeamName(teamId)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Location */}
              <div>
                <label className="block font-medium mb-2">Local <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  className="border w-full px-4 py-2 rounded-md"
                  value={matchLocation}
                  onChange={e => setMatchLocation(e.target.value)}
                  placeholder="Ex: Campo Universitário"
                />
              </div>

              {/* Start Time */}
              <div>
                <label className="block font-medium mb-2">Data e Hora <span className="text-red-500">*</span></label>
                <input
                  type="datetime-local"
                  className="border w-full px-4 py-2 rounded-md"
                  value={matchStartTime}
                  onChange={e => setMatchStartTime(e.target.value)}
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsAddMatchModal(false);
                  setMatchTeamHome('');
                  setMatchTeamAway('');
                  setMatchLocation('');
                  setMatchStartTime('');
                  setError('');
                }}
                className="flex-1 bg-gray-300 hover:bg-gray-400 py-2 rounded-md transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateMatch}
                disabled={!matchTeamHome || !matchTeamAway || !matchLocation || !matchStartTime}
                className="flex-1 bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Criar Jogo
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default TorneioDetails;
