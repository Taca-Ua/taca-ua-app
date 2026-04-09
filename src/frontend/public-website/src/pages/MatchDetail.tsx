import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { matchesApi, type MatchDetail } from '../api';

function MatchDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await matchesApi.getById(id);
        setMatch(data);
      } catch (err) {
        console.error('Failed to load match:', err);
        setError('Erro ao carregar jogo.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-PT', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('pt-PT', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      finished: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    const statusLabels: Record<string, string> = {
      scheduled: 'Agendado',
      in_progress: 'Em Curso',
      finished: 'Finalizado',
      cancelled: 'Cancelado',
    };
    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}
      >
        {statusLabels[status] || status}
      </span>
    );
  };

  const getParticipantResult = (participantId: string) => {
    if (!match?.results) return null;
    return match.results.find((r) => r.participant_id === participantId) ?? null;
  };

  const getTitle = () => {
    if (!match || !match.participants || match.participants.length === 0) return 'Jogo';
    if (match.participant_count > 4) return match.tournament_name;
    return match.participants.map((p) => p.participant_name || 'Participante').join(' vs ');
  };

  const participantLink = (p: Record<string, any>) =>
    p.participant_type === 'team'
      ? `/equipas/${p.participant_entity_id}`
      : `/estudantes/${p.participant_entity_id}`;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-4xl mx-auto">
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2 text-sm text-gray-500">
            <Link to="/calendario" className="hover:text-teal-600">
              Calendário
            </Link>
            <span>/</span>
            <span className="text-gray-700">Detalhe do Jogo</span>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar jogo...</p>
            </div>
          ) : match ? (
            <>
              {/* Header card */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-800 leading-tight">
                    {getTitle()}
                  </h1>
                  {getStatusBadge(match.status)}
                </div>

                <div className="flex flex-wrap items-center gap-2 text-sm mb-4">
                  {match.modality_name && (
                    <span className="text-teal-600 font-medium">{match.modality_name}</span>
                  )}
                  {match.modality_name && <span className="text-gray-300">•</span>}
                  <Link
                    to={`/torneios/${match.tournament_id}`}
                    className="text-gray-500 hover:text-teal-600"
                  >
                    {match.tournament_name}
                  </Link>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Data</p>
                    <p className="font-medium text-gray-700 capitalize">
                      {formatDate(match.start_time)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Hora</p>
                    <p className="font-medium text-gray-700">{formatTime(match.start_time)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Local</p>
                    <p className="font-medium text-gray-700">{match.location || '—'}</p>
                  </div>
                </div>
              </div>

              {/* Participants & Scores */}
              {match.participants && match.participants.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h2 className="text-lg font-semibold text-gray-800 mb-5">
                    {match.participants.length === 2 ? 'Confronto' : 'Participantes'}
                  </h2>

                  {match.participants.length === 2 ? (
                    /* Head-to-head layout */
                    <div className="flex items-start gap-4">
                      {/* Participant 1 */}
                      <div className="flex-1 text-left">
                        <Link
                          to={participantLink(match.participants[0])}
                          className="font-semibold text-gray-800 hover:text-teal-600 text-lg leading-tight"
                        >
                          {match.participants[0].participant_name}
                        </Link>
                        {(() => {
                          const r = getParticipantResult(match.participants[0].participant_id);
                          if (!r) return null;
                          if (r.score !== null && r.score !== undefined)
                            return <p className="text-4xl font-bold text-teal-600 mt-2">{r.score}</p>;
                          if (r.position !== null && r.position !== undefined)
                            return (
                              <p className="mt-2 text-sm text-gray-500 font-medium">{r.position}º lugar</p>
                            );
                          return null;
                        })()}
                      </div>

                      <div className="text-2xl font-bold text-gray-400 pt-1 flex-shrink-0">vs</div>

                      {/* Participant 2 */}
                      <div className="flex-1 text-right">
                        <Link
                          to={participantLink(match.participants[1])}
                          className="font-semibold text-gray-800 hover:text-teal-600 text-lg leading-tight"
                        >
                          {match.participants[1].participant_name}
                        </Link>
                        {(() => {
                          const r = getParticipantResult(match.participants[1].participant_id);
                          if (!r) return null;
                          if (r.score !== null && r.score !== undefined)
                            return <p className="text-4xl font-bold text-teal-600 mt-2">{r.score}</p>;
                          if (r.position !== null && r.position !== undefined)
                            return (
                              <p className="mt-2 text-sm text-gray-500 font-medium">{r.position}º lugar</p>
                            );
                          return null;
                        })()}
                      </div>
                    </div>
                  ) : (
                    /* Multi-participant list layout */
                    <div className="space-y-3">
                      {match.participants.map((p) => {
                        const result = getParticipantResult(p.participant_id);
                        return (
                          <div
                            key={p.participant_id}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <Link
                              to={participantLink(p)}
                              className="font-medium text-gray-800 hover:text-teal-600"
                            >
                              {p.participant_name}
                            </Link>
                            {result && (
                              <div className="text-right flex items-center gap-2">
                                {result.score !== null && result.score !== undefined && (
                                  <span className="font-bold text-teal-600 text-lg">
                                    {result.score} pts
                                  </span>
                                )}
                                {result.position !== null && result.position !== undefined && (
                                  <span className="px-2 py-0.5 bg-gray-200 text-gray-600 rounded-full text-xs font-semibold">
                                    {result.position}º lugar
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Back link */}
              <Link to="/calendario" className="text-teal-600 hover:text-teal-700 text-sm font-medium">
                ← Voltar ao Calendário
              </Link>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Jogo não encontrado.</p>
              <Link to="/calendario" className="text-teal-600 hover:text-teal-700 mt-4 inline-block">
                Voltar ao Calendário
              </Link>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default MatchDetailPage;
