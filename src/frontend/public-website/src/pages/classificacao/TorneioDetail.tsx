import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import { api } from '../../api';
import type { TournamentPublicDetail } from '../../api/types';

function TorneioDet() {
  const { id } = useParams();
  const [tournament, setTournament] = useState<TournamentPublicDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch tournament details on mount
  useEffect(() => {
    if (!id) return;

    const loadTournament = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await api.tournaments.getTournamentDetail(id, true);
        setTournament(data);
      } catch (err) {
        console.error('Failed to load tournament:', err);
        setError('Erro ao carregar torneio');
      } finally {
        setLoading(false);
      }
    };

    loadTournament();
  }, [id]);

  const rankings = tournament?.rankings || [];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
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
              <p className="mt-4 text-gray-600">A carregar torneio...</p>
            </div>
          ) : tournament ? (
            <>
              {/* Header */}
              <div className="mb-8">
                <h1 className="text-4xl md:text-5xl font-bold text-gray-800">
                  {tournament.name}
                </h1>
                <div className="flex items-center gap-3 mt-2">
                  <p className="text-xl text-teal-600">{tournament.modality.name}</p>
                  <span className="text-gray-400">•</span>
                  <p className="text-xl text-gray-600">Época {tournament.season.year}</p>
                  <span className="text-gray-400">•</span>
                  <p className="text-sm text-gray-500 capitalize">{tournament.status}</p>
                </div>
                {tournament.rules && (
                  <p className="text-sm text-gray-600 mt-2">{tournament.rules}</p>
                )}
              </div>

              {/* Rankings Table */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          Posição
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          Equipa
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
                          <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                            Ainda não há classificação para este torneio.
                          </td>
                        </tr>
                      ) : (
                        rankings.map((entry, index) => (
                          <tr
                            key={entry.team_id}
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
                            <td className="px-6 py-4 text-lg font-medium text-gray-900">
                              {entry.team_name}
                            </td>
                            <td className="px-6 py-4">
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {entry.course_short_code}
                                </div>
                                <div className="text-xs text-gray-500">
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
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-xl text-gray-500">Torneio não encontrado.</p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default TorneioDet;
