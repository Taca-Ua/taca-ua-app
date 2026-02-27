import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from "../../components/nucleo_navbar";
import { studentsApi } from '../../api/members';
import { teamsApi } from '../../api/teams';
import { matchesApi } from '../../api/matches';
import { useAuth } from '../../hooks/useAuth';

function DashboardNucleo() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    members: 0,
    teams: 0,
    matches: 0,
    upcomingMatches: 0,
  });
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

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Núcleo</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{user?.full_name}</span> ({user?.course_abbreviation})
          </p>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div
                  onClick={() => navigate('/nucleo/membros')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Membros</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.members}</p>
                  <p className="text-sm text-gray-500 mt-2">Membros registados</p>
                </div>

                <div
                  onClick={() => navigate('/nucleo/equipas')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Equipas</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.teams}</p>
                  <p className="text-sm text-gray-500 mt-2">Equipas criadas</p>
                </div>

                <div
                  onClick={() => navigate('/nucleo/jogos')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Jogos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.matches}</p>
                  <p className="text-sm text-gray-500 mt-2">Total de jogos</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-2 text-orange-600">Próximos Jogos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.upcomingMatches}</p>
                  <p className="text-sm text-gray-500 mt-2">Jogos agendados</p>
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
