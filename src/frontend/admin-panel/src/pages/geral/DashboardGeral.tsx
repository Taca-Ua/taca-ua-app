import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from "../../components/geral_navbar";
import { modalitiesApi } from '../../api/modalities';
import { teamsApi } from '../../api/teams';
import { tournamentsApi } from '../../api/tournaments';
import { useAuth } from '../../hooks/useAuth';

function DashboardGeral() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    modalities: 0,
    courses: 0,
    tournaments: 0,
    activeTournaments: 0,
    teams: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);

        // Fetch all data in parallel
        const [modalities, tournaments, teams] = await Promise.all([
          modalitiesApi.getAll(),
          tournamentsApi.getAll(),
          teamsApi.getAll(true), // Get teams from all courses
        ]);

        // Count unique courses from teams
        const uniqueCourses = new Set(teams.map(t => t.course_id));

        // Count active tournaments
        const activeTournaments = tournaments.filter(t => t.status === 'active').length;

        setStats({
          modalities: modalities.length,
          courses: uniqueCourses.size,
          tournaments: tournaments.length,
          activeTournaments,
          teams: teams.length,
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
      <Sidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Geral</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{user?.full_name}</span>
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
                  onClick={() => navigate('/geral/modalidades')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Modalidades</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.modalities}</p>
                  <p className="text-sm text-gray-500 mt-2">Modalidades registadas</p>
                </div>

                <div
                  onClick={() => navigate('/geral/torneios')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-purple-600">Torneios</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.tournaments}</p>
                  <p className="text-sm text-gray-500 mt-2">Total de torneios</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-2 text-orange-600">Torneios Ativos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.activeTournaments}</p>
                  <p className="text-sm text-gray-500 mt-2">Em andamento</p>
                </div>

                <div
                  onClick={() => navigate('/geral/nucleos')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Núcleos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.courses}</p>
                  <p className="text-sm text-gray-500 mt-2">Núcleos ativos</p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-800">Ações Rápidas</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <button
                    onClick={() => navigate('/geral/modalidades')}
                    className="px-6 py-4 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">⚽ Gerir Modalidades</div>
                    <div className="text-sm opacity-90">Ver e editar modalidades</div>
                  </button>

                  <button
                    onClick={() => navigate('/geral/torneios')}
                    className="px-6 py-4 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">🏆 Gerir Torneios</div>
                    <div className="text-sm opacity-90">Criar e gerir torneios</div>
                  </button>

                  <button
                    onClick={() => navigate('/geral/regulamentos')}
                    className="px-6 py-4 bg-purple-500 hover:bg-purple-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">📋 Regulamentos</div>
                    <div className="text-sm opacity-90">Ver e editar regulamentos</div>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => navigate('/geral/nucleos')}
                    className="px-6 py-4 bg-green-500 hover:bg-green-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">🏫 Gerir Núcleos</div>
                    <div className="text-sm opacity-90">Ver núcleos e cursos</div>
                  </button>

                  <button
                    onClick={() => navigate('/geral/administradores')}
                    className="px-6 py-4 bg-orange-500 hover:bg-orange-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">👥 Administradores</div>
                    <div className="text-sm opacity-90">Gerir administradores</div>
                  </button>

                  <button
                    onClick={() => window.open('/', '_blank')}
                    className="px-6 py-4 bg-gray-500 hover:bg-gray-600 text-white rounded-md font-medium transition-colors text-left"
                  >
                    <div className="text-lg font-bold mb-1">🌐 Website Público</div>
                    <div className="text-sm opacity-90">Ver site público</div>
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

export default DashboardGeral;
