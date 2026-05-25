import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import { rankingApi, type GeneralRanking } from '../../api';
import { type SeasonDetail, seasonsApi } from '../../api/seasons';

function GeneralRankingPage() {
  const [rankings, setRankings] = useState<GeneralRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [seasonFilter, setSeasonFilter] = useState<number | null>(null);
  const [seasons, setSeasons] = useState<SeasonDetail[]>([]);

  useEffect(() => {
    seasonsApi.getAll().then((data) => {
      setSeasons(data.items);
      const active = data.items.find((s) => s.is_active);
      const defaultSeason = active ?? data.items[0];
      if (defaultSeason) setSeasonFilter(defaultSeason.season_id);
    })
    .catch((err) => {
      console.error('Error fetching seasons:', err);
      setError('Erro ao carregar temporadas. Por favor, tente novamente.');
    });
  }, []);

  useEffect(() => {
    if (seasonFilter === null) return;

    const fetchRankings = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await rankingApi.getGeneralRanking({
          season_id: seasonFilter,
        });
        setRankings(data.items);
      } catch (err) {
        console.error('Error fetching rankings:', err);
        setError('Erro ao carregar ranking geral. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, [seasonFilter]);

  const getMedalIcon = (rank: number | null) => {
    if (rank === null) return null;

    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return null;
    }
  };

  const getRankDisplay = (rank: number | null) => {
    if (rank === null) return '-';
    return `${rank}º`;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Ranking Geral
            </h1>
            <p className="text-lg text-gray-600">
              Classificação geral dos cursos com base nos resultados dos torneios
            </p>
          </div>

          {/* Filters */}
          <div className="flex flex-col md:flex-row md:items-center md:gap-6 mb-6">
          {/* Season Filter */}
          <div className="mb-6">
            <label htmlFor="season-filter" className="block text-sm font-medium text-gray-700 mb-2">
              Filtrar por Temporada
            </label>
            <select
              id="season-filter"
              value={seasonFilter!}
              onChange={(e) => setSeasonFilter(parseInt(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              {seasons.map((season) => (
                <option key={season.season_id} value={season.season_id}>
                  {season.name}
                </option>
              ))}
            </select>
          </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar ranking...</p>
            </div>
          ) : (
            <>
              {/* Rankings Table */}
              {rankings.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                  <p className="text-gray-500">Não há ranking disponível no momento.</p>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  {/* Desktop Table View */}
                  <div className="hidden md:block overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Posição
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Curso
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Núcleo
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Pontos
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {rankings.map((ranking) => (
                          <tr
                            key={ranking.id}
                            className={`hover:bg-gray-50 transition-colors ${
                              ranking.rank && ranking.rank <= 3 ? 'bg-yellow-50' : ''
                            }`}
                          >
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">{getMedalIcon(ranking.rank)}</span>
                                <span className="text-lg font-bold text-gray-900">
                                  {getRankDisplay(ranking.rank)}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm font-medium text-gray-900">
                                {ranking.course_name}
                              </div>
                              <div className="text-xs text-gray-500">
                                {ranking.course_abbreviation}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm text-gray-900">{ranking.nucleo_name}</div>
                              <div className="text-xs text-gray-500">
                                {ranking.nucleo_abbreviation}
                              </div>
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="text-lg font-bold text-teal-600">
                                {ranking.points}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Mobile Card View */}
                  <div className="md:hidden divide-y divide-gray-200">
                    {rankings.map((ranking) => (
                      <div
                        key={ranking.id}
                        className={`p-4 ${
                          ranking.rank && ranking.rank <= 3 ? 'bg-yellow-50' : ''
                        }`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{getMedalIcon(ranking.rank)}</span>
                            <span className="text-xl font-bold text-gray-900">
                              {getRankDisplay(ranking.rank)}
                            </span>
                          </div>
                          <span className="text-2xl font-bold text-teal-600">
                            {ranking.points} pts
                          </span>
                        </div>

                        <div className="space-y-2">
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {ranking.course_name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {ranking.course_abbreviation}
                            </p>
                          </div>

                          <div>
                            <p className="text-sm text-gray-700">{ranking.nucleo_name}</p>
                            <p className="text-xs text-gray-500">
                              {ranking.nucleo_abbreviation}
                            </p>
                          </div>

                          <div className="pt-2 border-t border-gray-200">
                            <p className="text-xs text-gray-600">
                              Torneios: {ranking.tournaments_participated}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default GeneralRankingPage;
