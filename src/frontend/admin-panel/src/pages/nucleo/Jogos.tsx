import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchesApi, type MatchListItem } from '../../api/matches';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';

const Jogos = () => {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [tournamentMap, setTournamentMap] = useState<Record<string, TournamentListItem>>({});
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedDay, setSelectedDay] = useState<Date>(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  });
  const [dayPage, setDayPage] = useState(1);

  // Fetch matches and tournaments from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [fetchedMatches, fetchedTournaments] = await Promise.all([
          matchesApi.getAll(),
          tournamentsApi.getAll(),
        ]);
        setMatches(fetchedMatches);
        const map: Record<string, TournamentListItem> = {};
        fetchedTournaments.forEach(t => { map[t.id] = t; });
        setTournamentMap(map);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        notify('Não foi possível carregar os jogos do núcleo. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Helper function to format match date/time
  const formatDateTime = (startTime: string) => {
    const date = new Date(startTime);
    return {
      date: date.toLocaleDateString('pt-PT'),
      time: date.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  // Helper function to get status display
  const getStatusDisplay = (status: string) => {
    const statusMap: Record<string, string> = {
      scheduled: 'Agendado',
      in_progress: 'Em curso',
      finished: 'Terminado',
      cancelled: 'Cancelado',
    };
    return statusMap[status] || status;
  };

  // Calendar helper functions
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    return { daysInMonth, startingDayOfWeek };
  };

  const getMatchesForDay = (day: number) => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();

    return matches.filter(match => {
      const matchDate = new Date(match.start_time);
      return matchDate.getDate() === day &&
             matchDate.getMonth() === month &&
             matchDate.getFullYear() === year;
    });
  };

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const monthName = currentMonth.toLocaleDateString('pt-PT', { month: 'long', year: 'numeric' });

  const getStatusDotColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-500';
      case 'in_progress': return 'bg-amber-500';
      case 'finished': return 'bg-green-500';
      case 'cancelled': return 'bg-red-400';
      default: return 'bg-gray-400';
    }
  };

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-800">Jogos</h1>

            <div className="flex flex-wrap gap-2 items-center">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="all">Todos os estados</option>
                <option value="scheduled">Agendado</option>
                <option value="in_progress">Em curso</option>
                <option value="finished">Terminado</option>
                <option value="cancelled">Cancelado</option>
              </select>

              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    viewMode === 'list'
                      ? 'bg-teal-500 text-white'
                      : btn.secondaryAlt
                  }`}
                >
                  Lista
                </button>
                <button
                  onClick={() => setViewMode('calendar')}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    viewMode === 'calendar'
                      ? 'bg-teal-500 text-white'
                      : btn.secondaryAlt
                  }`}
                >
                  Calendário
                </button>
              </div>
            </div>
          </div>

          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {!loading && (
            <>
              {viewMode === 'list' && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="space-y-3">
                    {(() => {
                      const filteredMatches = statusFilter === 'all'
                        ? matches
                        : matches.filter(m => m.status === statusFilter);
                      return filteredMatches.length > 0 ? (
                        filteredMatches.map((match) => {
                          const { date, time } = formatDateTime(match.start_time);
                          const tournament = tournamentMap[match.tournament_id];
                          return (
                            <button
                              key={match.id}
                              type="button"
                              onClick={() => navigate(`/jogos/${match.id}`)}
                              className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                            >
                              <div className="flex justify-between items-start mb-2">
                                <span className="text-gray-800 font-bold text-lg">
                                  {match.participants.map(p => p.name || 'TBD').join(' vs ')}
                                </span>
                                <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                                  match.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                                  match.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
                                  match.status === 'finished' ? 'bg-green-100 text-green-700' :
                                  'bg-red-100 text-red-700'
                                }`}>
                                  {getStatusDisplay(match.status)}
                                </span>
                              </div>
                              {tournament && (
                                <div className="flex gap-2 mb-2 text-sm">
                                  <span className="text-teal-600 font-medium">{tournament.name}</span>
                                  {tournament.modality && (
                                    <>
                                      <span className="text-gray-400">·</span>
                                      <span className="text-gray-500">{tournament.modality.name}</span>
                                    </>
                                  )}
                                </div>
                              )}
                              <div className="flex gap-6 text-sm text-gray-600">
                                <span>
                                  <span className="font-medium">Data:</span> {date}
                                </span>
                                <span>
                                  <span className="font-medium">Hora:</span> {time}
                                </span>
                                <span>
                                  <span className="font-medium">Local:</span> {match.location}
                                </span>
                              </div>
                            </button>
                          );
                        })
                      ) : (
                        <p className="text-gray-500 text-center py-8">
                          Nenhum jogo encontrado.
                        </p>
                      );
                    })()}
                  </div>
                </div>
              )}

              {viewMode === 'calendar' && (
                <div className="flex flex-col lg:flex-row gap-6">
                  {/* Calendar Grid */}
                  <div className="lg:w-3/5 bg-white rounded-lg shadow-md overflow-hidden">
                    <div className="flex justify-between items-center px-6 py-4 bg-gray-50 border-b">
                      <button
                        onClick={previousMonth}
                        className={`px-4 py-2 ${btn.secondaryAlt} rounded-md font-medium transition-colors`}
                      >
                        ←
                      </button>
                      <h2 className="text-xl font-bold text-gray-800 capitalize">
                        {monthName}
                      </h2>
                      <button
                        onClick={nextMonth}
                        className={`px-4 py-2 ${btn.secondaryAlt} rounded-md font-medium transition-colors`}
                      >
                        →
                      </button>
                    </div>

                    <div className="p-4">
                      <div className="grid grid-cols-7 mb-2">
                        {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map((day) => (
                          <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
                            {day}
                          </div>
                        ))}
                      </div>
                      <div className="grid grid-cols-7 gap-1">
                        {(() => {
                          const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);
                          const cells = [];
                          for (let i = 0; i < startingDayOfWeek; i++) {
                            cells.push(<div key={`empty-${i}`} className="aspect-square" />);
                          }
                          for (let day = 1; day <= daysInMonth; day++) {
                            const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
                            date.setHours(0, 0, 0, 0);
                            const dayMatches = getMatchesForDay(day);
                            const uniqueStatuses = [...new Set(dayMatches.map(m => m.status))];
                            const isTodayDay =
                              day === new Date().getDate() &&
                              currentMonth.getMonth() === new Date().getMonth() &&
                              currentMonth.getFullYear() === new Date().getFullYear();
                            const isSelected =
                              selectedDay.getDate() === day &&
                              selectedDay.getMonth() === currentMonth.getMonth() &&
                              selectedDay.getFullYear() === currentMonth.getFullYear();
                            cells.push(
                              <button
                                key={day}
                                type="button"
                                onClick={() => { setSelectedDay(date); setDayPage(1); }}
                                className={`aspect-square flex flex-col items-center justify-center rounded-lg border-2 transition-colors ${
                                  isSelected
                                    ? 'border-teal-500 bg-teal-50'
                                    : isTodayDay
                                    ? 'border-teal-200 bg-teal-50/50 hover:border-teal-400'
                                    : 'border-transparent hover:border-gray-300 bg-white'
                                }`}
                              >
                                <span className={`text-sm font-semibold ${
                                  isSelected || isTodayDay ? 'text-teal-600' : 'text-gray-700'
                                }`}>
                                  {day}
                                </span>
                                {uniqueStatuses.length > 0 && (
                                  <div className="mt-0.5 flex gap-0.5">
                                    {uniqueStatuses.slice(0, 3).map(status => (
                                      <span
                                        key={status}
                                        className={`w-2 h-2 rounded-full ${getStatusDotColor(status)} inline-block`}
                                      ></span>
                                    ))}
                                  </div>
                                )}
                              </button>
                            );
                          }
                          return cells;
                        })()}
                      </div>
                    </div>

                    {/* Legend */}
                    <div className="px-6 py-3 bg-gray-50 border-t flex flex-wrap items-center gap-4 text-xs text-gray-600">
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
                        Agendado
                      </span>
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-amber-500 inline-block"></span>
                        Em curso
                      </span>
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
                        Terminado
                      </span>
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-red-400 inline-block"></span>
                        Cancelado
                      </span>
                    </div>
                  </div>

                  {/* Side Panel */}
                  <div className="lg:w-2/5">
                    <div className="bg-white rounded-lg shadow-md p-5 sticky top-4">
                      <h3 className="text-lg font-bold text-gray-800 mb-1 capitalize">
                        {selectedDay.toLocaleDateString('pt-PT', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                      </h3>
                      {(() => {
                        const dayMatches = matches.filter(m => {
                          const d = new Date(m.start_time);
                          return d.getDate() === selectedDay.getDate() &&
                                 d.getMonth() === selectedDay.getMonth() &&
                                 d.getFullYear() === selectedDay.getFullYear();
                        });
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
                              {paginated.map((match) => {
                                const { time } = formatDateTime(match.start_time);
                                const tournament = tournamentMap[match.tournament_id];
                                return (
                                  <button
                                    key={match.id}
                                    type="button"
                                    onClick={() => navigate(`/jogos/${match.id}`)}
                                    className="w-full text-left p-3 bg-gray-50 rounded-lg hover:bg-teal-50 transition-colors border border-transparent hover:border-teal-200"
                                  >
                                    <div className="flex justify-between items-start mb-1">
                                      <span className="font-semibold text-sm text-gray-800">{time}</span>
                                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                                        match.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                                        match.status === 'in_progress' ? 'bg-amber-100 text-amber-700' :
                                        match.status === 'finished' ? 'bg-green-100 text-green-700' :
                                        'bg-red-100 text-red-700'
                                      }`}>
                                        {getStatusDisplay(match.status)}
                                      </span>
                                    </div>
                                    <p className="text-sm text-gray-700">
                                      {match.participants.map(p => p.name || 'TBD').join(' vs ')}
                                    </p>
                                    {tournament && (
                                      <p className="text-xs text-teal-600 mt-0.5">{tournament.name}</p>
                                    )}
                                    <p className="text-xs text-gray-500 mt-0.5">{match.location}</p>
                                  </button>
                                );
                              })}
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
          )}
        </div>
      </div>
  );
};

export default Jogos;
