import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchesApi, type MatchListItem } from '../../api/matches';
import { useAuth } from '../../hooks/useAuth';
import { seasonsApi, type SeasonSummary } from '../../api/seasons';
import { useSeason } from '../../contexts/SeasonContext';
import SeasonSelector from '../../components/seasons/SeasonSelector';

const MatchCalendar = () => {

  const navigate = useNavigate();
  const [allMatches, setAllMatches] = useState<MatchListItem[]>([]);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState<Date>(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  });
  const [dayPage, setDayPage] = useState(1);

  useEffect(() => {
    matchesApi.getAll().then(matches => {
      setAllMatches(matches);
    }).catch(err => {
      console.error('Failed to fetch matches for calendar:', err);
    });
  }, []);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    return {
      daysInMonth: lastDay.getDate(),
      startingDayOfWeek: firstDay.getDay()
    };
  };

  const getMatchesForDay = (day: number) => {
    return allMatches.filter(match => {
      const d = new Date(match.start_time);
      return d.getDate() === day &&
             d.getMonth() === currentMonth.getMonth() &&
             d.getFullYear() === currentMonth.getFullYear();
    });
  };

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const getStatusDotColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-500';
      case 'in_progress': return 'bg-amber-500';
      case 'finished': return 'bg-green-500';
      case 'cancelled': return 'bg-red-400';
      default: return 'bg-gray-400';
    }
  };

  const monthName = currentMonth.toLocaleDateString('pt-PT', { month: 'long', year: 'numeric' });

  return (
    <div className="bg-white rounded-lg shadow-md p-6 my-8">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={previousMonth}
            className="p-1.5 hover:bg-gray-100 rounded-md transition-colors text-gray-600"
          >
            ←
          </button>
          <h2 className="text-xl font-semibold text-teal-600 capitalize">
            {monthName}
          </h2>
          <button
            onClick={nextMonth}
            className="p-1.5 hover:bg-gray-100 rounded-md transition-colors text-gray-600"
          >
            →
          </button>
        </div>
        <button
          onClick={() => navigate("/jogos")}
          className="text-teal-600 hover:underline text-sm font-medium"
        >
          Ver todos →
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Calendar Grid */}
        <div className="lg:w-3/5">
          <div className="grid grid-cols-7 mb-2">
            {["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"].map((d) => (
              <div
                key={d}
                className="text-center text-xs font-bold text-gray-400 pb-2"
              >
                {d}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1">
            {(() => {
              const { daysInMonth, startingDayOfWeek } =
                getDaysInMonth(currentMonth);
              const cells = [];
              for (let i = 0; i < startingDayOfWeek; i++) {
                cells.push(
                  <div key={`empty-${i}`} className="aspect-square" />,
                );
              }
              for (let day = 1; day <= daysInMonth; day++) {
                const date = new Date(
                  currentMonth.getFullYear(),
                  currentMonth.getMonth(),
                  day,
                );
                date.setHours(0, 0, 0, 0);
                const dayMatches = getMatchesForDay(day);
                const uniqueStatuses = [
                  ...new Set(dayMatches.map((m) => m.status)),
                ];
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
                    onClick={() => {
                      setSelectedDay(date);
                      setDayPage(1);
                    }}
                    className={`aspect-square flex flex-col items-center justify-center rounded-md border-2 transition-colors ${
                      isSelected
                        ? "border-teal-500 bg-teal-50"
                        : isTodayDay
                          ? "border-teal-200 bg-teal-50/50 hover:border-teal-400"
                          : "border-transparent hover:border-gray-200 bg-white"
                    }`}
                  >
                    <span
                      className={`text-xs font-semibold ${
                        isSelected || isTodayDay
                          ? "text-teal-600"
                          : "text-gray-500"
                      }`}
                    >
                      {day}
                    </span>
                    {uniqueStatuses.length > 0 && (
                      <div className="mt-0.5 flex gap-0.5">
                        {uniqueStatuses.slice(0, 3).map((status) => (
                          <span
                            key={status}
                            className={`w-1.5 h-1.5 rounded-full ${getStatusDotColor(status)} inline-block`}
                          ></span>
                        ))}
                      </div>
                    )}
                  </button>,
                );
              }
              return cells;
            })()}
          </div>
          {/* Legend */}
          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
              Agendado
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block"></span>
              Em curso
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
              Terminado
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-400 inline-block"></span>
              Cancelado
            </span>
          </div>
        </div>
        <div className="lg:w-2/5">
          <h4 className="text-sm font-bold text-gray-700 mb-2 capitalize">
            {selectedDay.toLocaleDateString("pt-PT", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </h4>
          {(() => {
            const dayMatches = allMatches.filter((m) => {
              const d = new Date(m.start_time);
              return (
                d.getDate() === selectedDay.getDate() &&
                d.getMonth() === selectedDay.getMonth() &&
                d.getFullYear() === selectedDay.getFullYear()
              );
            });
            const GAMES_PER_PAGE = 10;
            const totalDayPages = Math.ceil(dayMatches.length / GAMES_PER_PAGE);
            const paginated = dayMatches.slice(
              (dayPage - 1) * GAMES_PER_PAGE,
              dayPage * GAMES_PER_PAGE,
            );
            if (dayMatches.length === 0) {
              return (
                <p className="text-gray-400 text-xs py-4 text-center">
                  Sem jogos neste dia.
                </p>
              );
            }
            return (
              <>
                <div className="space-y-2">
                  {paginated.map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => navigate(`/jogos/${m.id}`)}
                      className="w-full text-left p-2 bg-gray-50 rounded-md hover:bg-teal-50 transition-colors border border-transparent hover:border-teal-200"
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-xs font-semibold text-gray-700">
                          {new Date(m.start_time).toLocaleTimeString("pt-PT", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                            m.status === "scheduled"
                              ? "bg-blue-100 text-blue-700"
                              : m.status === "in_progress"
                                ? "bg-amber-100 text-amber-700"
                                : m.status === "finished"
                                  ? "bg-green-100 text-green-700"
                                  : "bg-red-100 text-red-700"
                          }`}
                        >
                          {m.status === "scheduled"
                            ? "Agendado"
                            : m.status === "in_progress"
                              ? "Em curso"
                              : m.status === "finished"
                                ? "Terminado"
                                : "Cancelado"}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mt-0.5 truncate">
                        {m.participants
                          .map((p) => p.name || "TBD")
                          .join(" vs ")}
                      </p>
                    </button>
                  ))}
                </div>
                {totalDayPages > 1 && (
                  <div className="mt-3 flex justify-between items-center">
                    <button
                      onClick={() => setDayPage((p) => Math.max(1, p - 1))}
                      disabled={dayPage === 1}
                      className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                    >
                      ←
                    </button>
                    <span className="text-xs text-gray-500">
                      {dayPage}/{totalDayPages}
                    </span>
                    <button
                      onClick={() =>
                        setDayPage((p) => Math.min(totalDayPages, p + 1))
                      }
                      disabled={dayPage === totalDayPages}
                      className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                    >
                      →
                    </button>
                  </div>
                )}
              </>
            );
          })()}
        </div>
      </div>
    </div>
  );
}


function DashboardNucleo() {
  const navigate = useNavigate();
  const { username } = useAuth();
  const { loadedSeason } = useSeason();

  const [seasonStatistics, setSeasonStatistics] = useState<SeasonSummary | null>(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [seasonStats] = await Promise.all([
          seasonsApi.getSeasonSummary(loadedSeason?.id || -1),
        ]);

        setSeasonStatistics(seasonStats);

      } catch (err) {
        console.error('Failed to fetch dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    };

    console.log('Mounting DashboardNucleo, fetching stats...');
    fetchStats();
  }, [loadedSeason?.id]);

  if (loading) {
    return (
      <div className="flex-1 p-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  return (
    <>
      <SeasonSelector />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{username ?? 'Administrador'}</span>
          </p>

          {/* Main Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <button
              type="button"
              onClick={() => navigate('/cursos')}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left w-full focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <h2 className="text-sm font-semibold text-purple-600 uppercase tracking-wide mb-3">Cursos</h2>
              <p className="text-4xl font-bold text-gray-800 mb-1">{seasonStatistics?.active_courses_count ?? 0}</p>
              <p className="text-xs text-gray-500">Ativos nesta época</p>
            </button>

            <button
              type="button"
              onClick={() => navigate('/teams')}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <h2 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">Equipas</h2>
              <p className="text-4xl font-bold text-gray-800 mb-1">{seasonStatistics?.teams_count ?? 0}</p>
              <p className="text-xs text-gray-500">Total registadas</p>
            </button>
          </div>

          <MatchCalendar />

          {/* Tournaments Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Torneios</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
                <p className="text-sm text-orange-700 font-semibold">Em Andamento</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">{seasonStatistics?.tournaments_summary.ongoing ?? 0}</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                <p className="text-sm text-green-700 font-semibold">Finalizados</p>
                <p className="text-3xl font-bold text-green-900 mt-2">{seasonStatistics?.tournaments_summary.finished ?? 0}</p>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                <p className="text-sm text-blue-700 font-semibold">Agendados</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">{seasonStatistics?.tournaments_summary.scheduled ?? 0}</p>
              </div>
              <button
                type="button"
                onClick={() => navigate('/torneios')}
                className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg hover:shadow-md transition-shadow text-left focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <p className="text-sm text-purple-700 font-semibold">Total</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {(seasonStatistics?.tournaments_summary.ongoing ?? 0) + (seasonStatistics?.tournaments_summary.finished ?? 0) + (seasonStatistics?.tournaments_summary.scheduled ?? 0)}
                </p>
              </button>
            </div>
          </div>

          {/* Matches & Members Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Jogos</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-orange-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Em Andamento</span>
                  <span className="text-2xl font-bold text-orange-600">{seasonStatistics?.matches_summary.ongoing ?? 0}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Agendados</span>
                  <span className="text-2xl font-bold text-blue-600">{seasonStatistics?.matches_summary.scheduled ?? 0}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Finalizados</span>
                  <span className="text-2xl font-bold text-green-600">{seasonStatistics?.matches_summary.finished ?? 0}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Membros</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-indigo-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Atletas</span>
                  <span className="text-2xl font-bold text-indigo-600">{seasonStatistics?.members_summary.athletes ?? 0}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-slate-50 rounded">
                  <span className="text-sm font-medium text-gray-700">Staff</span>
                  <span className="text-2xl font-bold text-slate-600">{seasonStatistics?.members_summary.staff ?? 0}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-100 rounded">
                  <span className="text-sm font-medium text-gray-700">Total</span>
                  <span className="text-2xl font-bold text-gray-800">{(seasonStatistics?.members_summary.athletes ?? 0) + (seasonStatistics?.members_summary.staff ?? 0)}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </>
  );
}

export default DashboardNucleo;
