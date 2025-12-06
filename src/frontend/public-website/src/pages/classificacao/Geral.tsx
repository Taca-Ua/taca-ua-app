import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import { api } from '../../api';
import type { Season, GeneralRankingResponse } from '../../api/types';

function ClassificacaoGeral() {
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [selectedSeasonId, setSelectedSeasonId] = useState<string>('');
  const [rankingData, setRankingData] = useState<GeneralRankingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch seasons on mount
  useEffect(() => {
    const loadSeasons = async () => {
      try {
        const seasonsData = await api.seasons.getSeasons();
        setSeasons(seasonsData);

        // Set active season as default
        const activeSeason = seasonsData.find(s => s.status === 'active');
        if (activeSeason) {
          setSelectedSeasonId(String(activeSeason.id));
        } else if (seasonsData.length > 0) {
          setSelectedSeasonId(String(seasonsData[0].id));
        }
      } catch (err) {
        console.error('Failed to load seasons:', err);
        setError('Erro ao carregar épocas');
      }
    };

    loadSeasons();
  }, []);

  // Fetch rankings when season changes
  useEffect(() => {
    if (!selectedSeasonId) return;

    const loadRankings = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await api.rankings.getGeneralRanking(Number(selectedSeasonId));
        setRankingData(data);
      } catch (err) {
        console.error('Failed to load rankings:', err);
        setError('Erro ao carregar classificação');
      } finally {
        setLoading(false);
      }
    };

    loadRankings();
  }, [selectedSeasonId]);

  const rankings = rankingData?.rankings || [];

  const selectedSeasonDisplayName = seasons.find(s => String(s.id) === String(selectedSeasonId))?.year?.toString() || (rankingData ? `${rankingData.season_year}` : '');

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-2 text-gray-800">
            Classificação Geral
          </h1>
          {selectedSeasonDisplayName && (
            <p className="text-sm text-gray-600 mb-6">Época: {selectedSeasonDisplayName}</p>
          )}

          {/* Época Filter */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Época
            </label>
            <select
              value={selectedSeasonId}
              onChange={(e) => setSelectedSeasonId(e.target.value)}
              className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
              disabled={loading}
            >
              {seasons.map((season) => (
                <option key={season.id} value={season.id}>
                  Época {season.year}
                </option>
              ))}
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar classificação...</p>
            </div>
          ) : (
            /* Rankings Table */
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                        Posição
                      </th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                        Curso
                      </th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                        J
                      </th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                        V
                      </th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                        E
                      </th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                        D
                      </th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">
                        Pontos
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {rankings.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                          Ainda não há dados de classificação para esta época.
                        </td>
                      </tr>
                    ) : (
                      rankings.map((entry, index) => (
                        <tr
                          key={entry.course_id}
                          className={`hover:bg-gray-50 transition-colors ${
                            index === 0 ? 'bg-yellow-50' : ''
                          }`}
                        >
                          <td className="px-6 py-4">
                            <span
                              className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                                index === 0
                                  ? 'bg-yellow-400 text-yellow-900'
                                  : 'bg-gray-200 text-gray-700'
                              }`}
                            >
                              {entry.position}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div>
                              <div className="text-lg font-medium text-gray-900">
                                {entry.course_short_code}
                              </div>
                              <div className="text-sm text-gray-500">
                                {entry.course_name}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center text-gray-700">
                            {entry.played}
                          </td>
                          <td className="px-6 py-4 text-center text-green-600 font-medium">
                            {entry.won}
                          </td>
                          <td className="px-6 py-4 text-center text-gray-600">
                            {entry.drawn}
                          </td>
                          <td className="px-6 py-4 text-center text-red-600 font-medium">
                            {entry.lost}
                          </td>
                          <td className="px-6 py-4 text-right text-lg font-bold text-gray-900">
                            {entry.points}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default ClassificacaoGeral;
