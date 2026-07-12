import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import { tournamentsApi, matchesApi, type TournamentDetail as TournamentDetailType, type TournamentStanding, type MatchDetail } from '../../api';

const StandingsTableEntry = ({ standing }: { standing: TournamentStanding }) => {
  const stats = standing.statistics_metadata || {} as {
    points: number;
    wins: number;
    draws: number;
    losses: number;
    scored_points: number;
    conceded_points: number;
    differential: number;
  };

  const participantLink = (p: Record<string, any>) => {
    if (!p) return '#';

    switch (p.competitor_type) {
      case 'team':
        return `/equipas/${p.competitor_entity_id}`;
      default:
        return '#';
    }
  }

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4">
        <span className="font-semibold text-gray-700">
          {standing.position || '-'}º
        </span>
      </td>
      <td className="px-6 py-4">
        <Link
          to={participantLink(standing)}
          className="text-teal-600 hover:text-teal-700 font-medium"
        >
          {standing.competitor_name}
        </Link>
        <p className="text-xs text-gray-500 capitalize">
          {standing.competitor_type === 'team' ? 'Equipa' : 'Atleta'}
        </p>
      </td>
      <td className="px-6 py-4 text-right">
        <span className="font-bold text-lg text-teal-600">
          {stats.points ?? '-'}
        </span>
      </td>
      <td className="px-6 py-4 text-center text-green-600 font-medium">
        {stats.wins ?? '-'}
      </td>
      <td className="px-6 py-4 text-center text-gray-600">
        {stats.draws ?? '-'}
      </td>
      <td className="px-6 py-4 text-center text-red-600 font-medium">
        {stats.losses ?? '-'}
      </td>
    </tr>
  );
}

const StandingsTable = ({ standings }: { standings: TournamentStanding[] }) => {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                Posição
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                Competidor
              </th>
              <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">
                Pontos
              </th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                V
              </th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                E
              </th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                D
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {standings.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                  Ainda não há classificação para este torneio.
                </td>
              </tr>
            ) : (
              [...standings]
                .sort((a, b) => {
                  const rankA = a.position ?? Infinity;
                  const rankB = b.position ?? Infinity;
                  if (rankA !== rankB) return rankA - rankB;
                  return (b.position ?? 0) - (a.position ?? 0);
                })
                .map((standing, index) => (
                  <StandingsTableEntry key={index} standing={standing} />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}


function TournamentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [tournament, setTournament] = useState<TournamentDetailType | null>(null);
  const [standings, setStandings] = useState<TournamentStanding[]>([]);
  const [matches, setMatches] = useState<MatchDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'standings' | 'matches'>('standings');

  useEffect(() => {
    if (!id) return;

    const loadTournamentData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [tournamentData, standingsData, matchesData] = await Promise.all([
          tournamentsApi.getById(id),
          tournamentsApi.getStandings(id, { page_size: 100 }),
          matchesApi.getAll({ tournament_id: id, page_size: 100 }),
        ]);

        setTournament(tournamentData);
        setStandings(standingsData.items);
        setMatches(matchesData.items);
      } catch (err) {
        console.error('Failed to load tournament:', err);
        setError('Erro ao carregar torneio');
      } finally {
        setLoading(false);
      }
    };

    loadTournamentData();
  }, [id]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-PT', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-PT', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-green-100 text-green-800',
      finished: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800',
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
    };

    const statusLabels = {
      draft: 'Rascunho',
      active: 'Ativo',
      finished: 'Finalizado',
      cancelled: 'Cancelado',
      scheduled: 'Agendado',
      in_progress: 'Em Curso',
    };

    const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
    const label = statusLabels[status as keyof typeof statusLabels] || status;

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
        {label}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar torneio...</p>
            </div>
          ) : tournament ? (
            <>
              {/* Header */}
              <div className="mb-8">
                <div className="flex items-start justify-between mb-4">
                  <h1 className="text-4xl md:text-5xl font-bold text-gray-800">
                    {tournament.tournament_name}
                  </h1>
                  {getStatusBadge(tournament.status)}
                </div>

                <div className="flex flex-wrap items-center gap-3 text-lg">
                  <p className="text-teal-600 font-medium">
                    {tournament.modality_name || tournament.modality_type_name}
                  </p>
                  <span className="text-gray-400">•</span>
                  <p className="text-gray-600">{formatDate(tournament.start_date)}</p>
                </div>

                <div className="mt-4 flex gap-6">
                  <div>
                    <p className="text-sm text-gray-500">Competidores</p>
                    <p className="text-2xl font-semibold text-gray-800">{tournament.competitor_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Jogos</p>
                    <p className="text-2xl font-semibold text-gray-800">{tournament.match_count}</p>
                  </div>
                </div>
              </div>

              {/* Tabs */}
              <div className="mb-6 border-b border-gray-200">
                <div className="flex gap-8">
                  <button
                    onClick={() => setActiveTab('standings')}
                    className={`pb-4 px-1 font-semibold border-b-2 transition-colors ${
                      activeTab === 'standings'
                        ? 'border-teal-600 text-teal-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Classificação
                  </button>
                  <button
                    onClick={() => setActiveTab('matches')}
                    className={`pb-4 px-1 font-semibold border-b-2 transition-colors ${
                      activeTab === 'matches'
                        ? 'border-teal-600 text-teal-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Jogos ({matches.length})
                  </button>
                </div>
              </div>

              {/* Standings Tab */}
              {activeTab === 'standings' && (
                standings.length === 0 ? (
                  <div className="bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">Ainda não há classificação para este torneio.</p>
                  </div>
                ) : (
                  <StandingsTable standings={standings} />
                )
              )}

              {/* Matches Tab */}
              {activeTab === 'matches' && (
                <div className="space-y-4">
                  {matches.length === 0 ? (
                    <div className="bg-white rounded-lg shadow p-8 text-center">
                      <p className="text-gray-500">Ainda não há jogos para este torneio.</p>
                    </div>
                  ) : (
                    matches.map((match) => (
                      <Link
                        key={match.match_id}
                        to={`/jogos/${match.match_id}`}
                        className="block bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-inherit"
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <p className="text-sm text-gray-500">
                              {formatDateTime(match.start_time)} • {match.location}
                            </p>
                          </div>
                          {getStatusBadge(match.status)}
                        </div>

                        {match.participants && match.participants.length > 0 && (
                          <div className="mb-3">
                            <div className="flex flex-wrap gap-2">
                              {match.participants.map((participant, idx) => (
                                <span
                                  key={idx}
                                  className="px-3 py-1 bg-gray-100 rounded-full text-sm"
                                >
                                  {participant.participant_name || 'Participante'}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {match.results && match.results.length > 0 && (
                          <div className="border-t pt-3">
                            <p className="text-sm font-semibold text-gray-700 mb-2">Resultados:</p>
                            <div className="space-y-1">
                              {match.results.map((result, idx) => {
                                const participant = match.participants?.find(
                                  (p: Record<string, any>) => p.participant_id === result.participant_id
                                );
                                const name = participant?.participant_name || 'Participante';
                                const hasScore = result.score !== undefined && result.score !== null;
                                return (
                                  <div key={idx} className="flex justify-between items-center text-sm">
                                    <span>{name}</span>
                                    {hasScore ? (
                                      <span className="font-semibold">{result.score} {tournament.modality_point_unit || "pt"}{result.score > 1 ? 's' : ''}</span>
                                    ) : result.position !== undefined && result.position !== null ? (
                                      <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold">
                                        {result.position}º lugar
                                      </span>
                                    ) : null}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        </Link>
                    ))
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Torneio não encontrado</p>
              <Link to="/torneios" className="text-teal-600 hover:text-teal-700 mt-4 inline-block">
                Voltar aos torneios
              </Link>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default TournamentDetailPage;
