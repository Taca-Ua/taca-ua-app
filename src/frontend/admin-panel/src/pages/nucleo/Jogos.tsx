import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { matchesApi } from '../../api/matches';
import type { Match } from '../../api/matches';
import { tournamentsApi } from '../../api/tournaments';
import type { Tournament } from '../../api/tournaments';
import { useNotification } from '../../contexts/NotificationProvider';

const Jogos = () => {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<Match[]>([]);
  const [tournamentMap, setTournamentMap] = useState<Record<string, Tournament>>({});
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [statusFilter, setStatusFilter] = useState<string>('all');

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
        const map: Record<string, Tournament> = {};
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

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />

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
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Lista
                </button>
                <button
                  onClick={() => setViewMode('calendar')}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    viewMode === 'calendar'
                      ? 'bg-teal-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
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
                              onClick={() => navigate(`/nucleo/jogos/${match.id}`)}
                              className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                            >
                              <div className="flex justify-between items-start mb-2">
                                <span className="text-gray-800 font-bold text-lg">
                                  {match.participants.map(p => {
                                    if (p.team) return p.team.name;
                                    if (p.athlete) return p.athlete.full_name;
                                    return 'TBD';
                                  }).join(' vs ')}
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
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex justify-between items-center mb-6">
                    <button
                      onClick={previousMonth}
                      className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md font-medium transition-colors"
                    >
                      ←
                    </button>
                    <h2 className="text-2xl font-bold text-gray-800 capitalize">
                      {monthName}
                    </h2>
                    <button
                      onClick={nextMonth}
                      className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md font-medium transition-colors"
                    >
                      →
                    </button>
                  </div>

                  <div className="grid grid-cols-7 gap-2">
                    {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map((day) => (
                      <div key={day} className="text-center font-bold text-gray-600 py-2">
                        {day}
                      </div>
                    ))}

                    {(() => {
                      const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);
                      const days = [];

                      // Empty cells for days before the first day of the month
                      for (let i = 0; i < startingDayOfWeek; i++) {
                        days.push(
                          <div key={`empty-${i}`} className="min-h-[100px] bg-gray-50 rounded-md" />
                        );
                      }

                      // Days of the month
                      for (let day = 1; day <= daysInMonth; day++) {
                        const dayMatches = getMatchesForDay(day);
                        const isToday =
                          day === new Date().getDate() &&
                          currentMonth.getMonth() === new Date().getMonth() &&
                          currentMonth.getFullYear() === new Date().getFullYear();

                        days.push(
                          <div
                            key={day}
                            className={`min-h-[100px] border rounded-md p-2 ${
                              isToday ? 'bg-teal-50 border-teal-500' : 'bg-white border-gray-200'
                            }`}
                          >
                            <div className={`font-bold mb-1 ${isToday ? 'text-teal-600' : 'text-gray-700'}`}>
                              {day}
                            </div>
                            <div className="space-y-1">
                              {dayMatches.map((match) => {
                                const { time } = formatDateTime(match.start_time);
                                return (
                                  <button
                                    key={match.id}
                                    type="button"
                                    onClick={() => navigate(`/nucleo/jogos/${match.id}`)}
                                    className="w-full text-left text-xs bg-teal-100 hover:bg-teal-200 px-2 py-1 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    title={`${time} - ${match.participants.map(p => {
                                      if (p.team) return p.team.name;
                                      if (p.athlete) return p.athlete.full_name;
                                      return 'TBD';
                                    }).join(' vs ')}`}
                                  >
                                    <div className="font-medium truncate">{time}</div>
                                    <div className="truncate text-gray-600">
                                      {match.participants.map(p => {
                                        if (p.team) return p.team.name;
                                        if (p.athlete) return p.athlete.full_name;
                                        return 'TBD';
                                      }).join(' vs ')}
                                    </div>
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        );
                      }

                      return days;
                    })()}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Jogos;
