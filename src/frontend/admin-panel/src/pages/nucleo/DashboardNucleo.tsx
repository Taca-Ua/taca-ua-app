import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { seasonsApi, type SeasonSummary } from '../../api/seasons';
import { useSeason } from '../../contexts/SeasonContext';
import SeasonSelector from '../../components/seasons/SeasonSelector';
import MatchesCalendarComponent from '../../components/matches/MatchesCalendarComponent';

function DashboardNucleo() {
  const navigate = useNavigate();
  const { username } = useAuth();
  const { loadedSeason } = useSeason();

  const [seasonStatistics, setSeasonStatistics] = useState<SeasonSummary | null>(null);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    seasonsApi.getSeasonSummary(loadedSeason?.id)
      .then(seasonStats => {
        setSeasonStatistics(seasonStats);
      }).catch(err => {
        console.error('Failed to fetch dashboard stats:', err);
      })
      .finally(() => {
        setLoading(false);
      });

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
              onClick={() => navigate('/equipas')}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <h2 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">Equipas</h2>
              <p className="text-4xl font-bold text-gray-800 mb-1">{seasonStatistics?.teams_count ?? 0}</p>
              <p className="text-xs text-gray-500">Total registadas</p>
            </button>
          </div>

          <MatchesCalendarComponent />

          {/* Tournaments Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8 mt-8">
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
