import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from "../../components/nucleo_navbar";
import { studentsApi } from '../../api/members';
import { teamsApi } from '../../api/teams';
import { matchesApi, type Match } from '../../api/matches';
import { useAuth } from '../../hooks/useAuth';

function DashboardNucleo() {
  const navigate = useNavigate();
  const { username } = useAuth();

  const [stats, setStats] = useState({
    members: 0,
    teams: 0,
    matches: 0,
    upcomingMatches: 0,
  });

  const [allMatches, setAllMatches] = useState<Match[]>([]);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [students, teams, matches] = await Promise.all([
          studentsApi.getAll(),
          teamsApi.getAll(),
          matchesApi.getAll(),
        ]);

        setAllMatches(matches);
        const upcomingMatches = matches.filter(m => m.status === 'scheduled').length;

        setStats({
          members: students.length,
          teams: teams.length,
          matches: matches.length,
          upcomingMatches,
        });
      } catch (err) {
        console.error('Failed to fetch dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
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

  const monthName = currentMonth.toLocaleDateString('pt-PT', { month: 'long', year: 'numeric' });

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{username ?? 'Administrador'}</span>
          </p>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <button onClick={() => navigate('/nucleo/membros')} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Membros</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.members}</p>
                  <p className="text-sm text-gray-500 mt-2">Membros registados</p>
                </button>
                <button onClick={() => navigate('/nucleo/equipas')} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Equipas</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.teams}</p>
                  <p className="text-sm text-gray-500 mt-2">Equipas criadas</p>
                </button>
                <button onClick={() => navigate('/nucleo/jogos')} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left">
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Jogos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.matches}</p>
                  <p className="text-sm text-gray-500 mt-2">Total de jogos</p>
                </button>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-2 text-orange-600">Próximos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.upcomingMatches}</p>
                  <p className="text-sm text-gray-500 mt-2">Jogos agendados</p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Agenda de Jogos - {monthName}</h2>
                  <button
                    onClick={() => navigate('/nucleo/jogos')}
                    className="text-teal-600 hover:underline text-sm font-medium"
                  >
                    Ver todos os detalhes →
                  </button>
                </div>

                <div className="grid grid-cols-7 gap-1">
                  {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(d => (
                    <div key={d} className="text-center text-xs font-bold text-gray-400 pb-2">{d}</div>
                  ))}

                  {(() => {
                    const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);
                    const days = [];
                    for (let i = 0; i < startingDayOfWeek; i++) {
                      days.push(<div key={`empty-${i}`} className="h-24 bg-gray-50/50 rounded-sm" />);
                    }
                    for (let day = 1; day <= daysInMonth; day++) {
                      const dayMatches = getMatchesForDay(day);
                      const isToday = day === new Date().getDate() && currentMonth.getMonth() === new Date().getMonth();

                      days.push(
                        <div key={day} className={`h-24 border border-gray-100 p-1 relative ${isToday ? 'bg-teal-50' : 'bg-white'}`}>
                          <span className={`text-xs font-semibold ${isToday ? 'text-teal-600' : 'text-gray-400'}`}>{day}</span>
                          <div className="mt-1 overflow-y-auto max-h-[60px] space-y-1">
                            {dayMatches.slice(0, 3).map(m => (
                              <div
                                key={m.id}
                                onClick={() => navigate(`/nucleo/jogos/${m.id}`)}
                                className="text-[9px] bg-teal-600 text-white p-0.5 rounded truncate cursor-pointer hover:bg-teal-700"
                              >
                                {new Date(m.start_time).toLocaleTimeString('pt-PT', {hour:'2-digit', minute:'2-digit'})} - {m.participants[0]?.team?.name || 'TBD'}
                              </div>
                            ))}
                            {dayMatches.length > 3 && <p className="text-[8px] text-center text-gray-400">+{dayMatches.length - 3} mais</p>}
                          </div>
                        </div>
                      );
                    }
                    return days;
                  })()}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashboardNucleo;
