import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { matchesApi, type MatchDetail } from '../api';

function Calendario() {
  const today = new Date();
  const [matches, setMatches] = useState<MatchDetail[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('calendar');
  const [searchQuery, setSearchQuery] = useState('');
  const [pageSize, setPageSize] = useState(20);
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [selectedDay, setSelectedDay] = useState<Date>(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  });
  const [dayPage, setDayPage] = useState(1);
  const [listTotalPages, setListTotalPages] = useState(1);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        // setLoading(true);
        setError(null);

        if (viewMode === 'list') {
          const response = await matchesApi.getAll({
            page,
            page_size: pageSize,
          });
          setMatches(response.items);
          setListTotalPages(Math.max(1, Math.ceil(response.total / pageSize)));
        };

        if (viewMode === 'calendar') {
          // Fetch all pages so search/calendar work across full dataset
          const PAGE_SIZE = 100;
          let date = `${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}`;
          const first = await matchesApi.getAll({
            page: 1,
            page_size: PAGE_SIZE,
            date: date, // Filter by current month for calendar view
          });

          const totalPages = Math.ceil(first.total / PAGE_SIZE);
          if (totalPages <= 1) {
            setMatches(first.items);
          } else {
            const rest = await Promise.all(
              Array.from({ length: totalPages - 1 }, (_, i) =>
                matchesApi.getAll({
                  page: i + 2,
                  page_size: PAGE_SIZE,
                  date: date
                })
              )
            );
            setMatches([...first.items, ...rest.flatMap(r => r.items)]);
          }
        }
      } catch (err) {
        console.error('Error fetching matches:', err);
        setError('Erro ao carregar jogos. Por favor, tente novamente.');
      } finally {
        // setLoading(false);
      }
    };

    fetchMatches();
  }, [viewMode, currentMonth, currentYear, pageSize, page]);

  useEffect(() => {
    // Reset to first page when view mode changes
    setPage(1);
  }, [viewMode]);

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
      finished: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
    };

    const statusLabels = {
      scheduled: 'Agendado',
      in_progress: 'Em Curso',
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

  const getParticipantName = (participant_id : string) => {
    const participant = matches.flatMap(m => m.participants || []).find(p => p.participant_id === participant_id);
    return participant ? (participant.participant_name || 'Participante') : 'Participante';
  };

  const filteredMatches = viewMode === 'list'
    ? matches.filter((m) =>
        getMatchTitle(m)?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (m.tournament_name?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)
      )
    : matches;

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

            {viewMode === 'list' && (
              <input
                type="text"
                placeholder="Pesquisar jogo ou torneio..."
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent w-full md:w-72"
              />
            )}

            {viewMode === 'list' && (
              <select
                value={pageSize}
                onChange={(e) => { setPageSize(parseInt(e.target.value)); setPage(1); }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              >
                <option value={10}>10 por página</option>
                <option value={20}>20 por página</option>
                <option value={50}>50 por página</option>
              </select>
            )}

          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {
            <>
              {/* List View */}
              {viewMode === 'list' && (
                <>
                  {/* Matches List */}
                  <div className="space-y-4">
                  {filteredMatches.length === 0 ? (
                    <div className="bg-white rounded-lg shadow p-8 text-center">
                      <p className="text-gray-500">Não há jogos disponíveis com os filtros selecionados.</p>
                    </div>
                  ) : (
                    filteredMatches.map((match) => (
                        <div
                          key={match.match_id}
                          className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
                        >
                          <div className="flex justify-between items-start mb-4">
                            <div className="flex-1">
                              <Link
                                to={`/jogos/${match.match_id}`}
                                className="block text-xl font-semibold text-gray-800 hover:text-teal-600 mb-1"
                              >
                                {getMatchTitle(match)}
                              </Link>
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
                                {match.participants.map((participant, idx) => {
                                  return (
                                  <span
                                    key={idx}
                                    className="px-3 py-1 bg-gray-100 rounded-full text-sm"
                                  >
                                    {participant.participant_name || 'Participante1'}
                                  </span>
                                )})}
                              </div>
                            </div>
                          )}

                          {match.results && match.results.length > 0 && (
                            <div className="border-t pt-4 mt-4">
                              <p className="text-sm font-semibold text-gray-700 mb-2">Resultados:</p>
                              <div className="space-y-1">
                                {match.results.map((result, idx) => (
                                  <div key={idx} className="flex justify-between text-sm">
                                    <span>{getParticipantName(result.participant_id)}</span>
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
                  {listTotalPages > 1 && (
                    <div className="mt-8 flex justify-center gap-2">
                      <button
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Anterior
                      </button>
                      <span className="px-4 py-2 text-gray-700">
                        Página {page} de {listTotalPages}
                      </span>
                      <button
                        onClick={() => setPage((p) => Math.min(listTotalPages, p + 1))}
                        disabled={page === listTotalPages}
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
                <div className="flex flex-col lg:flex-row gap-6">
                  {/* Calendar Grid */}
                  <div className="lg:w-3/5 bg-white rounded-lg shadow overflow-hidden">
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
                      <div className="grid grid-cols-7 mb-2">
                        {dayNames.map((day) => (
                          <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
                            {day}
                          </div>
                        ))}
                      </div>
                      <div className="grid grid-cols-7 gap-1">
                        {Array.from({ length: getFirstDayOfMonth(currentMonth, currentYear) }).map((_, idx) => (
                          <div key={`empty-${idx}`} className="aspect-square"></div>
                        ))}
                        {Array.from({ length: getDaysInMonth(currentMonth, currentYear) }).map((_, idx) => {
                          const day = idx + 1;
                          const date = new Date(currentYear, currentMonth, day);
                          date.setHours(0, 0, 0, 0);
                          const dayMatches = getMatchesForDate(date);
                          const isCurrentDay = isToday(day);
                          const isSelected =
                            selectedDay.getDate() === day &&
                            selectedDay.getMonth() === currentMonth &&
                            selectedDay.getFullYear() === currentYear;

                          return (
                            <button
                              key={day}
                              type="button"
                              onClick={() => { setSelectedDay(date); setDayPage(1); }}
                              className={`aspect-square flex flex-col items-center justify-center rounded-lg border-2 transition-colors ${
                                isSelected
                                  ? 'border-teal-500 bg-teal-50'
                                  : isCurrentDay
                                  ? 'border-teal-200 bg-teal-50/50 hover:border-teal-400'
                                  : 'border-transparent hover:border-gray-300 bg-white'
                              }`}
                            >
                              <span className={`text-sm font-semibold ${
                                isSelected || isCurrentDay ? 'text-teal-600' : 'text-gray-700'
                              }`}>
                                {day}
                              </span>
                              {dayMatches.length > 0 && (
                                <span className="mt-0.5 w-2 h-2 rounded-full bg-green-500 block"></span>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Legend */}
                    <div className="px-6 py-3 bg-gray-50 border-t flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
                        Com jogos
                      </span>
                    </div>
                  </div>

                  {/* Side Panel */}
                  <div className="lg:w-2/5">
                    <div className="bg-white rounded-lg shadow p-5 sticky top-4">
                      <h3 className="text-lg font-bold text-gray-800 mb-1 capitalize">
                        {selectedDay.toLocaleDateString('pt-PT', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                      </h3>
                      {(() => {
                        const dayMatches = getMatchesForDate(selectedDay);
                        const GAMES_PER_PAGE = 10;
                        const totalDayPages = Math.ceil(dayMatches.length / GAMES_PER_PAGE);
                        const paginated = dayMatches.slice(
                          (dayPage - 1) * GAMES_PER_PAGE,
                          dayPage * GAMES_PER_PAGE
                        );
                        if (dayMatches.length === 0) {
                          return (
                            <p className="text-gray-500 text-sm py-6 text-center">
                              Não há jogos neste dia.
                            </p>
                          );
                        }
                        return (
                          <>
                            <p className="text-sm text-gray-500 mb-3">{dayMatches.length} jogo{dayMatches.length !== 1 ? 's' : ''}</p>
                            <div className="space-y-2">
                              {paginated.map((match) => (
                                <Link
                                  key={match.match_id}
                                  to={`/jogos/${match.match_id}`}
                                  className="block p-3 bg-gray-50 rounded-lg hover:bg-teal-50 transition-colors border border-transparent hover:border-teal-200"
                                >
                                  <div className="flex justify-between items-start mb-1">
                                    <span className="font-semibold text-sm text-gray-800">
                                      {formatTime(match.start_time)}
                                    </span>
                                    {match.modality_name && (
                                      <span className="text-xs text-teal-600 font-medium">{match.modality_name}</span>
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-700">{getMatchTitle(match)}</p>
                                  <p className="text-xs text-gray-500 mt-0.5">{match.location}</p>
                                </Link>
                              ))}
                            </div>
                            {totalDayPages > 1 && (
                              <div className="mt-4 flex justify-between items-center">
                                <button
                                  onClick={() => setDayPage(p => Math.max(1, p - 1))}
                                  disabled={dayPage === 1}
                                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  Anterior
                                </button>
                                <span className="text-sm text-gray-600">{dayPage} / {totalDayPages}</span>
                                <button
                                  onClick={() => setDayPage(p => Math.min(totalDayPages, p + 1))}
                                  disabled={dayPage === totalDayPages}
                                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  Próxima
                                </button>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  </div>
                </div>
              )}
            </>
          }
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default Calendario;
