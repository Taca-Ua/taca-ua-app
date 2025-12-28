import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { tournamentsApi, type TournamentDetail, type TournamentUpdate } from '../../api/tournaments';
import { teamsApi, type Team } from '../../api/teams';
import { matchesApi, type Match, type MatchCreate } from '../../api/matches';

const TorneioDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [tournament, setTournament] = useState<TournamentDetail | null>(null);
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [isEditModal, setIsEditModal] = useState(false);
  const [isAddTeamModal, setIsAddTeamModal] = useState(false);
  const [isAddMatchModal, setIsAddMatchModal] = useState(false);
  const [isRankingModal, setIsRankingModal] = useState(false);

  // Campos edição
  const [editName, setEditName] = useState('');
  const [editStartDate, setEditStartDate] = useState('');

  // Novo team
  const [selectedTeamId, setSelectedTeamId] = useState('');

  // Novo match
  const [matchTeamHome, setMatchTeamHome] = useState('');
  const [matchTeamAway, setMatchTeamAway] = useState('');
  const [matchLocation, setMatchLocation] = useState('');
  const [matchStartTime, setMatchStartTime] = useState('');

  // Rankings
  const [rankings, setRankings] = useState<{ position: number; team_id: string }[]>([]);

  const fetchData = async () => {
    if (!id) return;

    try {
      setLoading(true);
      const [tournamentData, teamsData] = await Promise.all([
        tournamentsApi.getById(id),
        teamsApi.getAll(true), // Get all teams
      ]);
      setTournament(tournamentData);
      setAllTeams(teamsData);
      // Filter matches for this tournament
    //   const tournamentMatches = matchesData.filter(m => String(m.tournament_id) === id);
      const tournamentMatches = tournamentData.matches;
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

  // Get teams filtered by tournament modality
  const availableTeams = useMemo(() => {
    if (!tournament) return [];
    return allTeams.filter(team => team.modality_name === tournament.modality_name);
  }, [tournament, allTeams]);

  // Get current tournament teams
  const tournamentTeams = useMemo(() => {
    if (!tournament?.teams) return [];
    return tournament.teams.map(t => allTeams.find(team => team.id === t.id)).filter(Boolean) as Team[];
  }, [tournament, allTeams]);

  const openEdit = () => {
    if (!tournament) return;
    setEditName(tournament.name);
    setEditStartDate(tournament.start_date ?? '');
    setIsEditModal(true);
  };

  const saveEdit = async () => {
    if (!tournament) return;

    try {
      const updateData: TournamentUpdate = {
        name: editName,
        start_date: editStartDate || undefined,
      };
      const updated = await tournamentsApi.update(tournament.id, updateData);
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
      const updateData: TournamentUpdate = { status: 'active' };
      const updated = await tournamentsApi.update(tournament.id, updateData);
      setTournament(updated);
      setError('');
    } catch (err) {
      console.error('Failed to activate tournament:', err);
      setError('Erro ao ativar torneio');
    }
  };

  const openRankingModal = () => {
    if (!tournament) return;
    // Initialize rankings array based on ranking_positions
    const numPositions = tournament.ranking_positions || tournamentTeams.length;
    const initialRankings = Array.from({ length: numPositions }, (_, i) => ({
      position: i + 1,
      team_id: '',
    }));
    setRankings(initialRankings);
    setIsRankingModal(true);
  };

  const finishTournament = async () => {
    if (!tournament) return;

    // Check if we need to collect rankings
    if (tournament.ranking_positions && tournament.ranking_positions > 0) {
      openRankingModal();
    } else {
      // Finish without rankings
      if (!window.confirm("Finalizar torneio? Isso bloqueará edições.")) return;

      try {
        const finished = await tournamentsApi.finish(tournament.id);
        setTournament(finished);
        setError('');
      } catch (err) {
        console.error('Failed to finish tournament:', err);
        setError('Erro ao finalizar torneio');
      }
    }
  };

const submitRankings = async () => {
	if (!tournament) return;

	// Allow empty positions — only validate duplicates among filled positions
	const teamIds = rankings.map(r => r.team_id).filter(id => id);
	const uniqueTeamIds = new Set(teamIds);
	if (teamIds.length !== uniqueTeamIds.size) {
		alert('Cada equipa só pode aparecer uma vez no ranking.');
		return;
	}

	// filter out empty rankings
	const filteredRankings = rankings
		.filter(r => r.team_id)
		.map(r => ({ team_id: r.team_id, position: r.position }));

	try {
		const finished = await tournamentsApi.finish(tournament.id, filteredRankings);
		setTournament(finished);
		setIsRankingModal(false);
		setError('');
	} catch (err) {
		console.error('Failed to finish tournament:', err);
		setError('Erro ao finalizar torneio');
	}
};

  const addTeam = async () => {
    if (!tournament || !selectedTeamId) return;

    // Check if team is already added
    if (tournament.teams?.some(t => t.id === selectedTeamId)) {
      alert('Esta equipa já foi adicionada ao torneio.');
      return;
    }

    try {
      const updateData: TournamentUpdate = {
        teams_add: [selectedTeamId],
      };
      const updated = await tournamentsApi.update(tournament.id, updateData);
      setTournament(updated);
      setSelectedTeamId('');
      setIsAddTeamModal(false);
      setError('');
    } catch (err) {
      console.error('Failed to add team:', err);
      setError('Erro ao adicionar equipa');
    }
  };

  const removeTeam = async (teamId: string) => {
    if (!tournament) return;
    if (!window.confirm("Remover esta equipa do torneio?")) return;

    try {
      const updateData: TournamentUpdate = {
        teams_remove: [teamId],
      };
      const updated = await tournamentsApi.update(tournament.id, updateData);
      setTournament(updated);
      setError('');
    } catch (err) {
      console.error('Failed to remove team:', err);
      setError('Erro ao remover equipa');
    }
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
        tournament_id: String(tournament.id),
        team_home_id: String(matchTeamHome),
        team_away_id: String(matchTeamAway),
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
        <div className={`grid gap-8 ${tournament.final_rankings && tournament.final_rankings.length > 0 ? 'grid-cols-4' : 'grid-cols-3'}`}>

          {/* COL 1 - Detalhes */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Detalhes</h2>

            <div className="space-y-4">

              <div>
                <label className="font-medium text-teal-600">Nome</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.name}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Modalidade</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.modality_name}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Estado</label>
                <div className="bg-gray-100 p-3 rounded-md capitalize">{tournament.status}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Data de início</label>
                <div className="bg-gray-100 p-3 rounded-md">
                  {tournament.start_date ? new Date(tournament.start_date).toLocaleDateString('pt-PT') : "Não definida"}
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
              {tournamentTeams.length > 0 ? (
                tournamentTeams.map((team) => (
                  <div
                    key={team.id}
                    className="bg-gray-100 px-4 py-2 rounded-md text-gray-700 flex justify-between items-center"
                  >
                    <span>{team.name} ({team.course_name})</span>
                    {!isLocked && (
                      <button
                        onClick={() => removeTeam(team.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        Remover
                      </button>
                    )}
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
                matches.map(match => {
                  return (
                    <div
                      key={match.id}
                      onClick={() => navigate(`/geral/jogos/${match.id}`)}
                      className="bg-gray-100 px-4 py-3 rounded-md hover:bg-gray-200 cursor-pointer"
                    >
                      <div className="flex justify-between items-center">
                        <div className="text-sm font-medium">
                          {match.team_home_name || `Equipa X`} vs {match.team_away_name || `Equipa Y`}
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
                  );
                })
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

          {/* COL 4 - Rankings (only shown if tournament has final rankings) */}
          {tournament.final_rankings && tournament.final_rankings.length > 0 && (
            <div className="bg-white rounded-xl shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Classificação Final</h2>

              <div className="space-y-2">
                {tournament.final_rankings
                  .sort((a, b) => a.position - b.position)
                  .map((ranking) => (
                    <div
                      key={ranking.position}
                      className="bg-gradient-to-r from-teal-50 to-white px-4 py-3 rounded-md border border-teal-100"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`font-bold text-lg ${
                          ranking.position === 1 ? 'text-yellow-500' :
                          ranking.position === 2 ? 'text-gray-400' :
                          ranking.position === 3 ? 'text-amber-600' :
                          'text-gray-600'
                        }`}>
                          {ranking.position}º
                        </div>
                        <div className="text-gray-700 font-medium">
                          {ranking.team_name}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

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
                {availableTeams
                  .filter(team => !tournament?.teams?.some(t => t.id === team.id))
                  .map(team => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.course_name})
                    </option>
                  ))}
              </select>
              {availableTeams.filter(team => !tournament?.teams?.some(t => t.id === team.id)).length === 0 && (
                <p className="text-sm text-gray-500 mt-2 italic">
                  {availableTeams.length === 0
                    ? 'Nenhuma equipa disponível para esta modalidade'
                    : 'Todas as equipas desta modalidade já foram adicionadas'
                  }
                </p>
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
                  {tournamentTeams.map(team => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.course_name})
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
                  {tournamentTeams.map(team => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.course_name})
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
                  type="date"
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

      {/* ==================== MODAL RANKING ==================== */}
      {isRankingModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50 overflow-y-auto">
          <div className="bg-white p-8 rounded-lg max-w-2xl w-full my-8 mx-4">

            <h2 className="text-2xl font-bold mb-4">Classificação Final do Torneio</h2>
            <p className="text-gray-600 mb-6">
              Selecione a equipa para cada posição da classificação final.
            </p>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}

            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 mb-6">
              {rankings.map((ranking, index) => (
                <div key={ranking.position} className="flex items-center gap-4">
                  <div className={`font-bold text-lg w-12 text-center ${
                    ranking.position === 1 ? 'text-yellow-500' :
                    ranking.position === 2 ? 'text-gray-400' :
                    ranking.position === 3 ? 'text-amber-600' :
                    'text-gray-600'
                  }`}>
                    {ranking.position}º
                  </div>
                  <select
                    className="flex-1 border px-4 py-2 rounded-md bg-white"
                    value={ranking.team_id}
                    onChange={e => {
                      const newRankings = [...rankings];
                      newRankings[index].team_id = e.target.value;
                      setRankings(newRankings);
                    }}
                  >
                    <option value="">Selecionar equipa...</option>
                    {tournamentTeams.map(team => (
                      <option key={team.id} value={team.id}>
                        {team.name} ({team.course_name})
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsRankingModal(false);
                  setRankings([]);
                  setError('');
                }}
                className="flex-1 bg-gray-300 hover:bg-gray-400 py-2 rounded-md transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={submitRankings}
                className="flex-1 bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md transition-colors"
              >
                Finalizar Torneio
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default TorneioDetails;
