import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { matchesApi } from '../../api/matches';
import type { Match } from '../../api/matches';

const Jogos = () => {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // Fetch matches from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const fetchedMatches = await matchesApi.getAll();
        setMatches(fetchedMatches);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Erro ao carregar jogos. Por favor, tente novamente.');
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
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Jogos</h1>

            {/* View Mode Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-teal-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                📋 Lista
              </button>
              <button
                onClick={() => setViewMode('calendar')}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  viewMode === 'calendar'
                    ? 'bg-teal-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                📅 Calendário
              </button>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}

          {/* Content - Only show when not loading */}
          {!loading && !error && (
            <>
              {/* List View */}
              {viewMode === 'list' && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">Jogos</h2>
                  <div className="space-y-3">
                    {matches.length > 0 ? (
                      matches.map((match) => {
                        const { date, time } = formatDateTime(match.start_time);
                        return (
                          <div
                            key={match.id}
                            onClick={() => navigate(`/nucleo/jogos/${match.id}`)}
                            className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors"
                          >
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-gray-800 font-bold text-lg">
                                {match.team_home_name} vs {match.team_away_name}
                              </span>
                              <span className="text-teal-600 text-sm font-medium">
                                {getStatusDisplay(match.status)}
                              </span>
                            </div>
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
                              {match.home_score !== null && match.away_score !== null && (
                                <span>
                                  <span className="font-medium">Resultado:</span> {match.home_score} - {match.away_score}
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <p className="text-gray-500 text-center py-8">
                        Nenhum jogo encontrado.
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Calendar View */}
              {viewMode === 'calendar' && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  {/* Calendar Header */}
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

                  {/* Calendar Grid */}
                  <div className="grid grid-cols-7 gap-2">
                    {/* Day headers */}
                    {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map((day) => (
                      <div key={day} className="text-center font-bold text-gray-600 py-2">
                        {day}
                      </div>
                    ))}

                    {/* Calendar days */}
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
                                  <div
                                    key={match.id}
                                    onClick={() => navigate(`/nucleo/jogos/${match.id}`)}
                                    className="text-xs bg-teal-100 hover:bg-teal-200 px-2 py-1 rounded cursor-pointer transition-colors"
                                    title={`${time} - ${match.team_home_name} vs ${match.team_away_name}`}
                                  >
                                    <div className="font-medium truncate">{time}</div>
                                    <div className="truncate text-gray-600">
                                      {match.team_home_name} vs {match.team_away_name}
                                    </div>
                                  </div>
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
