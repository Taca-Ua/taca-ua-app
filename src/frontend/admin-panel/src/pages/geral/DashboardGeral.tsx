import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { modalitiesApi } from '../../api/modalities';
import { teamsApi } from '../../api/teams';
import { tournamentsApi } from '../../api/tournaments';
import { nucleosApi } from '../../api/nucleos';
import { useAuth } from '../../hooks/useAuth';
import { useSeason } from '../../contexts/SeasonContext';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import NewSeasonModal from '../../components/seasons/NewSeasonModal';

function DashboardGeral() {
  const navigate = useNavigate();
  // username is used in the welcome greeting below
  const { username } = useAuth();
  const { loadedSeason } = useSeason();
  const { pushModal } = useModal();

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
        const [modalities, tournaments, teams, nucleos] = await Promise.all([
          modalitiesApi.getAll({
            season_id: loadedSeason?.id,
          }),
          tournamentsApi.getAll({
            season_id: loadedSeason?.id,
          }),
          teamsApi.getAll(), // Get teams from all courses
          // seasonsApi.getAll(),
          nucleosApi.getAll(),
        ]);

        // Count active tournaments
        const activeTournaments = tournaments.filter(t => t.status === 'active').length;

        // Find current active season and draft season
        // const active = seasons.find(s => s.status === 'active') || null;
        // const draft = seasons.find(s => s.status === 'draft') || null;

        // setCurrentSeason(active);
        // setDraftSeason(draft);

        setStats({
          modalities: modalities.length,
          courses: nucleos.length,
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
  }, [loadedSeason?.id]);


  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Geral</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{username ?? 'Administrador'}</span>
          </p>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          ) : (
            <>
              <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-lg shadow-lg p-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold mb-2 text-gray-800">Gestão de Época</h2>
                    <Button
                      onClick={() => pushModal(
                        <NewSeasonModal />
                      )}
                      type='danger'
                    >
                      Finalizar Época Atual
                    </Button>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <button
                  type="button"
                  onClick={() => navigate('/modalidades')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Modalidades</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.modalities}</p>
                  <p className="text-sm text-gray-500 mt-2">Modalidades registadas</p>
                </button>

                <button
                  type="button"
                  onClick={() => navigate('/torneios')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <h2 className="text-xl font-semibold mb-2 text-purple-600">Torneios</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.tournaments}</p>
                  <p className="text-sm text-gray-500 mt-2">Total de torneios</p>
                </button>

                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-2 text-orange-600">Torneios Ativos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.activeTournaments}</p>
                  <p className="text-sm text-gray-500 mt-2">Em andamento</p>
                </div>

                <button
                  type="button"
                  onClick={() => navigate('/nucleos')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Núcleos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.courses}</p>
                  <p className="text-sm text-gray-500 mt-2">Núcleos ativos</p>
                </button>
              </div>

            </>
          )}
        </div>
      </div>
  );
}

export default DashboardGeral;
