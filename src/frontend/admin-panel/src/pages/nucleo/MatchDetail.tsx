import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { matchesApi } from '../../api/matches';
import type { Match, MatchLineup } from '../../api/matches';
import { teamsApi } from '../../api/teams';
import type { Team } from '../../api/teams';
import { useAuth } from '../../hooks/useAuth';

interface Lineup {
  player_id: string;
  jersey_number: number;
  is_starter: boolean;
}

const MatchDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [match, setMatch] = useState<Match | null>(null);
  const [teamHome, setTeamHome] = useState<Team | null>(null);
  const [teamAway, setTeamAway] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [userTeam, setUserTeam] = useState<'home' | 'away' | null>(null);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingTeam, setEditingTeam] = useState<'home' | 'away'>('home');
  const [selectedHomePlayers, setSelectedHomePlayers] = useState<Lineup[]>([]);
  const [selectedAwayPlayers, setSelectedAwayPlayers] = useState<Lineup[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;

      try {
        setLoading(true);
        console.log('Fetching match data for ID:', id);

        const [foundMatch] = await Promise.all([
          matchesApi.getById(id),
        ]);

        console.log('Match:', foundMatch);

        if (!foundMatch) {
          console.error('Match not found with ID:', id);
          navigate('/nucleo/jogos');
          return;
        }

        setMatch(foundMatch);

		const [homeTeam, awayTeam] = await Promise.all([
		  teamsApi.get(foundMatch.team_home_id),
		  teamsApi.get(foundMatch.team_away_id),
		]);

        setTeamHome(homeTeam || null);
        setTeamAway(awayTeam || null);

        // Initialize selected players from match lineup (default to empty)
        setSelectedHomePlayers(foundMatch.team_home?.lineup || []);
        setSelectedAwayPlayers(foundMatch.team_away?.lineup || []);

        // Determine which team belongs to the logged-in user
        if (user && homeTeam && awayTeam) {
          if (homeTeam.course_name === (user.course_abbreviation || '')) {
            setUserTeam('home');
          } else if (awayTeam.course_name === (user.course_abbreviation || '')) {
            setUserTeam('away');
          } else {
            setUserTeam(null);
          }
        }
      } catch (error) {
        console.error('Failed to fetch match data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, navigate, user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8 flex items-center justify-center">
          <div className="text-gray-600">A carregar...</div>
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            Jogo não encontrado. ID: {id}
          </div>
        </div>
      </div>
    );
  }

  if (!teamHome || !teamAway) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8">
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
            <p>Equipas não encontradas para este jogo.</p>
            <p className="text-sm mt-2">Team Home: {match.team_home_name} - Found: {teamHome ? 'Sim' : 'Não'}</p>
            <p className="text-sm">Team Away: {match.team_away_name} - Found: {teamAway ? 'Sim' : 'Não'}</p>
          </div>
        </div>
      </div>
    );
  }

  // Get selected players with lineup details from team's full player list
  const homePlayersList = selectedHomePlayers
    .map(lineup => {
      const player = teamHome?.players.find(p => p.id === lineup.player_id);
      return player ? { ...player, ...lineup } : null;
    })
    .filter((player): player is { id: string; full_name: string; jersey_number: number; is_starter: boolean; player_id: string } => player !== null);

  const awayPlayersList = selectedAwayPlayers
    .map(lineup => {
      const player = teamAway?.players.find(p => p.id === lineup.player_id);
      return player ? { ...player, ...lineup } : null;
    })
    .filter((player): player is { id: string; full_name: string; jersey_number: number; is_starter: boolean; player_id: string } => player !== null);

  const matchDateTime = new Date(match.start_time);
  const matchDate = matchDateTime.toLocaleDateString('pt-PT');
  const matchTime = matchDateTime.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });

  const handleSaveTeamMembers = async () => {
    if (!match || !teamHome || !teamAway) return;

    try {
      const lineup: MatchLineup = {
        team_id: editingTeam === 'home' ? teamHome.id : teamAway.id,
        players: editingTeam === 'home' ? selectedHomePlayers : selectedAwayPlayers,
      };

      await matchesApi.submitLineup(match.id, lineup);
      setIsEditModalOpen(false);
      setSearchQuery('');
      alert('Equipa de jogo guardada com sucesso!');
    } catch (error) {
      console.error('Failed to save lineup:', error);
      alert('Erro ao guardar escalação');
    }
  };

  const toggleTeamMember = (playerId: string) => {
    if (editingTeam === 'home') {
      const existingIndex = selectedHomePlayers.findIndex(p => p.player_id === playerId);
      if (existingIndex >= 0) {
        setSelectedHomePlayers(selectedHomePlayers.filter(p => p.player_id !== playerId));
      } else {
        setSelectedHomePlayers([...selectedHomePlayers, { player_id: playerId, jersey_number: 0, is_starter: false }]);
      }
    } else {
      const existingIndex = selectedAwayPlayers.findIndex(p => p.player_id === playerId);
      if (existingIndex >= 0) {
        setSelectedAwayPlayers(selectedAwayPlayers.filter(p => p.player_id !== playerId));
      } else {
        setSelectedAwayPlayers([...selectedAwayPlayers, { player_id: playerId, jersey_number: 0, is_starter: false }]);
      }
    }
  };

  const updatePlayerLineup = (playerId: string, field: 'jersey_number' | 'is_starter', value: number | boolean) => {
    if (editingTeam === 'home') {
      setSelectedHomePlayers(selectedHomePlayers.map(p =>
        p.player_id === playerId ? { ...p, [field]: value } : p
      ));
    } else {
      setSelectedAwayPlayers(selectedAwayPlayers.map(p =>
        p.player_id === playerId ? { ...p, [field]: value } : p
      ));
    }
  };

  const handleOpenEditModal = (team: 'home' | 'away') => {
    setEditingTeam(team);
    setSearchQuery('');
    setIsEditModalOpen(true);
  };

  const handleDownloadMatchSheet = async () => {
    try {
      const blob = await matchesApi.getMatchSheet(match.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ficha-jogo-${match.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download match sheet:', error);
      alert('Erro ao descarregar ficha de jogo');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Match Details */}
            <div className="bg-white rounded-lg shadow-md p-8">
              {/* Team Avatars */}
              <div className="flex justify-center items-center gap-8 mb-8">
                {/* Team 1 Avatar */}
                <div className="w-32 h-32 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
                  <svg
                    className="w-16 h-16 text-gray-700"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                  </svg>
                </div>

                {/* VS Text */}
                <div className="text-3xl font-bold text-gray-700">
                  VS
                </div>

                {/* Team 2 Avatar */}
                <div className="w-32 h-32 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
                  <svg
                    className="w-16 h-16 text-gray-700"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                  </svg>
                </div>
              </div>

              {/* Match Details Section */}
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-6">Detalhes do jogo</h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Equipa Casa
                    </label>
                    <div className="text-gray-800 font-medium">
                      {teamHome.name}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Equipa Visitante
                    </label>
                    <div className="text-gray-800 font-medium">
                      {teamAway.name}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Estado
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.status === 'scheduled' && '⏰ Agendado'}
                      {match.status === 'in_progress' && '▶️ Em curso'}
                      {match.status === 'finished' && '✅ Terminado'}
                      {match.status === 'cancelled' && '❌ Cancelado'}
                    </div>
                  </div>

                  {match.status === 'finished' && (match.home_score !== null || match.away_score !== null) && (
                    <div>
                      <label className="block text-gray-600 text-sm mb-1">
                        Resultado
                      </label>
                      <div className="text-gray-800 font-medium">
                        {teamHome.name}: {match.home_score ?? 0} - {teamAway.name}: {match.away_score ?? 0}
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Data e Hora
                    </label>
                    <div className="text-gray-800 font-medium">
                      {matchDate} às {matchTime}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Local
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.location}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Team Lineups */}
            <div className="bg-white rounded-lg shadow-md p-8 space-y-6">
              {/* Home Team Lineup */}
              <div className={userTeam === 'home' ? 'border-2 border-teal-500 rounded-lg p-4 -m-4 mb-2' : ''}>
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  Equipa de Jogo {teamHome.name}
                  {userTeam === 'home' && <span className="ml-2 text-teal-500 text-sm">(Minha Equipa)</span>}
                </h2>
                <div className="space-y-2 max-h-[250px] overflow-y-auto">
                  {homePlayersList.length > 0 ? (
                    homePlayersList.map((player) => (
                      <div
                        key={player.id}
                        className="px-4 py-2 bg-gray-100 rounded-md flex justify-between items-center"
                      >
                        <div className="flex items-center gap-3">
                          {player.is_starter && (
                            <span className="px-2 py-1 bg-teal-500 text-white text-xs rounded-full font-bold">T</span>
                          )}
                          <span className="text-gray-800 font-medium">{player.full_name}</span>
                        </div>
                        <span className="text-gray-600 text-sm font-semibold">#{player.jersey_number}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      Nenhum jogador na equipa de jogo.
                    </p>
                  )}
                </div>
              </div>

              {/* Away Team Lineup */}
              <div className={userTeam === 'away' ? 'border-2 border-teal-500 rounded-lg p-4 -m-4' : ''}>
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  Equipa de Jogo {teamAway.name}
                  {userTeam === 'away' && <span className="ml-2 text-teal-500 text-sm">(Minha Equipa)</span>}
                </h2>
                <div className="space-y-2 max-h-[250px] overflow-y-auto">
                  {awayPlayersList.length > 0 ? (
                    awayPlayersList.map((player) => (
                      <div
                        key={player.id}
                        className="px-4 py-2 bg-gray-100 rounded-md flex justify-between items-center"
                      >
                        <div className="flex items-center gap-3">
                          {player.is_starter && (
                            <span className="px-2 py-1 bg-teal-500 text-white text-xs rounded-full font-bold">T</span>
                          )}
                          <span className="text-gray-800 font-medium">{player.full_name}</span>
                        </div>
                        <span className="text-gray-600 text-sm font-semibold">#{player.jersey_number}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-4">
                      Nenhum jogador na equipa de jogo.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 mt-8">
            {match.status === 'scheduled' && (
              <>
                <button
                  className="flex-1 min-w-[200px] px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                  onClick={() => handleOpenEditModal('home')}
                >
                  Editar Equipa de Jogo {teamHome.name}
                </button>
                <button
                  className="flex-1 min-w-[200px] px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                  onClick={() => handleOpenEditModal('away')}
                >
                  Editar Equipa de Jogo {teamAway.name}
                </button>
              </>
            )}
            {match.status !== 'scheduled' && (
              <div className="flex-1 min-w-[200px] px-6 py-3 bg-gray-300 text-gray-600 rounded-md font-medium text-center">
                Não pode editar a equipa de jogo após o início do jogo
              </div>
            )}
            <button
              className="flex-1 min-w-[200px] px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-md font-medium transition-colors"
              onClick={handleDownloadMatchSheet}
            >
              Descarregar Ficha de Jogo
            </button>
          </div>
        </div>
      </div>

      {/* Edit Team Members Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 animate-slideUp max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">
              Editar Equipa de Jogo - {editingTeam === 'home' ? teamHome?.name : teamAway?.name}
            </h2>

            {/* Search Bar */}
            <div className="mb-4">
              <input
                type="text"
                placeholder="Procurar jogadores..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <div className="space-y-2 max-h-[500px] overflow-y-auto">
                {(() => {
                  const currentTeam = editingTeam === 'home' ? teamHome : teamAway;
                  const currentLineup = editingTeam === 'home' ? selectedHomePlayers : selectedAwayPlayers;
                  const filteredPlayers = currentTeam?.players.filter(player =>
                    player.full_name.toLowerCase().includes(searchQuery.toLowerCase())
                  ) || [];

                  return filteredPlayers.length > 0 ? (
                    filteredPlayers.map((player) => {
                      const lineupEntry = currentLineup.find(l => l.player_id === player.id);
                      const isSelected = !!lineupEntry;

                      return (
                        <div
                          key={`${editingTeam}-${player.id}`}
                          className="px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => toggleTeamMember(player.id)}
                              className="w-5 h-5 text-teal-500 rounded focus:ring-2 focus:ring-teal-500"
                            />
                            <span className="text-gray-800 flex-1 font-medium">{player.full_name}</span>
                          </div>
                          {isSelected && (
                            <div className="ml-8 flex gap-4 items-center">
                              <div className="flex items-center gap-2">
                                <label className="text-sm text-gray-600">Número:</label>
                                <input
                                  type="number"
                                  min="0"
                                  max="99"
                                  value={lineupEntry.jersey_number}
                                  onChange={(e) => updatePlayerLineup(player.id, 'jersey_number', parseInt(e.target.value) || 0)}
                                  className="w-16 px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                                  onClick={(e) => e.stopPropagation()}
                                />
                              </div>
                              <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                  type="checkbox"
                                  checked={lineupEntry.is_starter}
                                  onChange={(e) => updatePlayerLineup(player.id, 'is_starter', e.target.checked)}
                                  className="w-4 h-4 text-teal-500 rounded focus:ring-2 focus:ring-teal-500"
                                  onClick={(e) => e.stopPropagation()}
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
                  );
                })()}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsEditModalOpen(false);
                  setSearchQuery('');
                  // Reset to original lineup from match
                  if (match) {
                    setSelectedHomePlayers(match.team_home?.lineup || []);
                    setSelectedAwayPlayers(match.team_away?.lineup || []);
                  }
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveTeamMembers}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MatchDetail;
