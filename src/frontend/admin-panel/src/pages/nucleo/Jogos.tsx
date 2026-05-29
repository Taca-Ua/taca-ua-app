import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchesApi, type MatchListItem } from '../../api/matches';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';
import MatchesCalendarComponent from '../../components/matches/MatchesCalendarComponent';

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
                          const tournament = tournamentMap[match.tournament.id];
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
                <MatchesCalendarComponent />
              )}
            </>
          )}
        </div>
      </div>
  );
};

export default Jogos;
