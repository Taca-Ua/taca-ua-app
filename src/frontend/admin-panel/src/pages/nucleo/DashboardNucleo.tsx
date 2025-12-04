import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from "../../components/nucleo_navbar";
import { studentsApi } from '../../api/students';
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

        // Fetch all data in parallel
        const [students, teams, matches] = await Promise.all([
          studentsApi.getAll(),
          teamsApi.getAll(),
          matchesApi.getAll(),
        ]);

        // Count upcoming matches (scheduled)
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
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Núcleo</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{user?.full_name}</span> ({user?.course_abbreviation})
          </p>

          {/* Loading State */}
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          ) : (
            <>
              {/* Stats Cards */}
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

              {/* Quick Actions */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-800">Ações Rápidas</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => navigate('/nucleo/membros')}
                    className="px-6 py-4 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">➕ Adicionar Membro</div>
                    <div className="text-sm opacity-90">Registar novo jogador ou técnico</div>
                  </button>

                  <button
                    onClick={() => navigate('/nucleo/equipas')}
                    className="px-6 py-4 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">🏆 Criar Equipa</div>
                    <div className="text-sm opacity-90">Nova equipa para modalidade</div>
                  </button>

                  <button
                    onClick={() => navigate('/nucleo/jogos')}
                    className="px-6 py-4 bg-purple-500 hover:bg-purple-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">📅 Ver Jogos</div>
                    <div className="text-sm opacity-90">Consultar calendário de jogos</div>
                  </button>
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
