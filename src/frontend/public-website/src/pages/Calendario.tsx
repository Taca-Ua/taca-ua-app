import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { matchesApi, type MatchDetail } from '../api';

function Calendario() {
  const today = new Date();
  const [matches, setMatches] = useState<MatchDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          page: viewMode === 'calendar' ? 1 : page,
          page_size: viewMode === 'calendar' ? 100 : 20, // Fetch more for calendar view
          ...(statusFilter !== 'all' && { status: statusFilter }),
        };

        const data = await matchesApi.getAll(params);
        setMatches(data.items);
        setTotalPages(Math.ceil(data.total / data.page_size));
      } catch (err) {
        console.error('Error fetching matches:', err);
        setError('Erro ao carregar jogos. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, [page, statusFilter, viewMode]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-PT', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-PT', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      finished: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
    };

    const statusLabels = {
      scheduled: 'Agendado',
      in_progress: 'Em Curso',
      completed: 'Concluído',
      finished: 'Finalizado',
      cancelled: 'Cancelado',
    };

    const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
    const label = statusLabels[status as keyof typeof statusLabels] || status;

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
        {label}
      </span>
    );
  };

  // Calendar helper functions
  const monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

  const getDaysInMonth = (month: number, year: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (month: number, year: number) => {
    return new Date(year, month, 1).getDay();
  };

  const getMatchesForDate = (date: Date) => {
    return matches.filter(match => {
      const matchDate = new Date(match.start_time);
      return matchDate.getDate() === date.getDate() &&
             matchDate.getMonth() === date.getMonth() &&
             matchDate.getFullYear() === date.getFullYear();
    });
  };

  const nextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const prevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const isToday = (day: number) => {
    return day === today.getDate() &&
           currentMonth === today.getMonth() &&
           currentYear === today.getFullYear();
  };

  const getMatchTitle = (match: MatchDetail) => {
    // If there are more than 4 participants, show tournament name
    if (match.participant_count > 4 || !match.participants || match.participants.length === 0) {
      return match.tournament_name;
    }

    // Build "A vs B vs C" format
    const participantNames = match.participants.map(
      (p) => p.participant_name || 'Participante'
    );
    return participantNames.join(' vs ');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Calendário de Jogos
            </h1>
            <p className="text-lg text-gray-600">
              Veja todos os jogos programados e resultados
            </p>
          </div>

          {/* Filters */}
          <div className="mb-6 flex gap-4 flex-wrap items-center">
            {/* View Mode Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white text-teal-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Lista
              </button>
              <button
                onClick={() => setViewMode('calendar')}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  viewMode === 'calendar'
                    ? 'bg-white text-teal-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Calendário
              </button>
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="all">Todos os Estados</option>
              <option value="scheduled">Agendado</option>
              <option value="in_progress">Em Curso</option>
              <option value="completed">Concluído</option>
              <option value="finished">Finalizado</option>
              <option value="cancelled">Cancelado</option>
            </select>
          </div>

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
              <p className="mt-4 text-gray-600">A carregar jogos...</p>
            </div>
          ) : (
            <>
              {/* List View */}
              {viewMode === 'list' && (
                <>
                  {/* Matches List */}
                  <div className="space-y-4">
                    {matches.length === 0 ? (
                      <div className="bg-white rounded-lg shadow p-8 text-center">
                        <p className="text-gray-500">Não há jogos disponíveis com os filtros selecionados.</p>
                      </div>
                    ) : (
                      matches.map((match) => (
                        <div
                          key={match.match_id}
                          className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
                        >
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <h3 className="text-xl font-semibold text-gray-800 mb-1">
                                {getMatchTitle(match)}
                              </h3>
                              <Link
                                to={`/torneios/${match.tournament_id}`}
                                className="text-sm text-teal-600 hover:text-teal-700"
                              >
                                {match.tournament_name}
                              </Link>
                              {match.modality_name && (
                                <p className="text-sm text-gray-500 mt-1">{match.modality_name}</p>
                              )}
                            </div>
                            {getStatusBadge(match.status)}
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div>
                              <p className="text-sm text-gray-500">Data e Hora</p>
                              <p className="font-medium">
                                {formatDate(match.start_time)} às {formatTime(match.start_time)}
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-500">Local</p>
                              <p className="font-medium">{match.location}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-500">Participantes</p>
                              <p className="font-medium">{match.participant_count}</p>
                            </div>
                          </div>

                          {match.participants && match.participants.length > 0 && match.participant_count > 4 && (
                            <div className="border-t pt-4">
                              <p className="text-sm font-semibold text-gray-700 mb-2">Participantes:</p>
                              <div className="flex flex-wrap gap-2">
                                {match.participants.map((participant, idx) => (
                                  <span
                                    key={idx}
                                    className="px-3 py-1 bg-gray-100 rounded-full text-sm"
                                  >
                                    {participant.name || participant.team_name || 'Participante'}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {match.results && match.results.length > 0 && (
                            <div className="border-t pt-4 mt-4">
                              <p className="text-sm font-semibold text-gray-700 mb-2">Resultados:</p>
                              <div className="space-y-1">
                                {match.results.map((result, idx) => (
                                  <div key={idx} className="flex justify-between text-sm">
                                    <span>{result.name || result.team_name || 'Participante'}</span>
                                    <span className="font-semibold">
                                      {result.score !== undefined ? result.score : result.position}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="mt-8 flex justify-center gap-2">
                      <button
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Anterior
                      </button>
                      <span className="px-4 py-2 text-gray-700">
                        Página {page} de {totalPages}
                      </span>
                      <button
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Próxima
                      </button>
                    </div>
                  )}
                </>
              )}

              {/* Calendar View */}
              {viewMode === 'calendar' && (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  {/* Calendar Header */}
                  <div className="flex items-center justify-between px-6 py-4 bg-gray-50 border-b">
                    <button
                      onClick={prevMonth}
                      className="p-2 hover:bg-gray-200 rounded-md transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>
                    <h2 className="text-xl font-semibold text-gray-800">
                      {monthNames[currentMonth]} {currentYear}
                    </h2>
                    <button
                      onClick={nextMonth}
                      className="p-2 hover:bg-gray-200 rounded-md transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>

                  {/* Calendar Grid */}
                  <div className="p-4">
                    {/* Day Names */}
                    <div className="grid grid-cols-7 mb-2">
                      {dayNames.map((day) => (
                        <div
                          key={day}
                          className="text-center text-sm font-semibold text-gray-600 py-2"
                        >
                          {day}
                        </div>
                      ))}
                    </div>

                    {/* Calendar Days */}
                    <div className="grid grid-cols-7 gap-2">
                      {/* Empty cells for days before month starts */}
                      {Array.from({ length: getFirstDayOfMonth(currentMonth, currentYear) }).map((_, idx) => (
                        <div key={`empty-${idx}`} className="aspect-square"></div>
                      ))}

                      {/* Days of the month */}
                      {Array.from({ length: getDaysInMonth(currentMonth, currentYear) }).map((_, idx) => {
                        const day = idx + 1;
                        const date = new Date(currentYear, currentMonth, day);
                        const dayMatches = getMatchesForDate(date);
                        const isCurrentDay = isToday(day);

                        return (
                          <div
                            key={day}
                            className={`min-h-[85px] border rounded-lg p-1 ${
                              isCurrentDay
                                ? 'bg-teal-50 border-teal-500'
                                : 'bg-white border-gray-200 hover:border-gray-300'
                            } transition-colors overflow-hidden`}
                          >
                            <div className={`text-xs font-bold mb-1 px-1 ${
                              isCurrentDay ? 'text-teal-600' : 'text-gray-700'
                            }`}>
                              {day}
                            </div>
                            {dayMatches.length > 0 && (
                              <div className="flex flex-col gap-1">
                                {dayMatches.slice(0, 3).map((match) => (
                                  <Link
                                    key={match.match_id}
                                    to={`/torneios/${match.tournament_id}`}
                                    className="block text-[10px] leading-tight bg-teal-100 text-teal-800 px-1.5 py-0.5 rounded truncate hover:bg-teal-200 transition-colors"
                                    title={`${match.modality_name || 'Jogo'}: ${match.tournament_name}`}
                                  >
                                    <span className="font-semibold">{formatTime(match.start_time)}</span>
                                    {match.modality_name && (
                                      <span className="opacity-75"> - {match.modality_name}</span>
                                    )}
                                  </Link>
                                ))}
                                {dayMatches.length > 3 && (
                                  <div className="text-[9px] text-gray-500 px-1 font-medium italic">
                                    +{dayMatches.length - 3} mais...
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Calendar Legend */}
                  <div className="px-6 py-4 bg-gray-50 border-t">
                    <p className="text-sm text-gray-600">
                      <span className="inline-block w-3 h-3 bg-teal-100 rounded mr-2"></span>
                      Jogos agendados
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default Calendario;
