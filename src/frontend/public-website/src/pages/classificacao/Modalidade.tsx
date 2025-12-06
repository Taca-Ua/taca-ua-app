import { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import TournamentCard from '../../components/TournamentCard';
import { api } from '../../api';
import type { Season, Modality, TournamentPublicDetail } from '../../api/types';

function ClassificacaoModalidade() {
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [selectedSeasonId, setSelectedSeasonId] = useState<string>('');
  const [selectedModalityId, setSelectedModalityId] = useState<string>('');
  const [tournaments, setTournaments] = useState<TournamentPublicDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch seasons and modalities on mount
  useEffect(() => {
    const loadFilters = async () => {
      try {
        const [seasonsData, modalitiesData] = await Promise.all([
          api.seasons.getSeasons(),
          api.modalities.getModalities(),
        ]);

        setSeasons(seasonsData);
        setModalities(modalitiesData);

        // Set active season as default
        const activeSeason = seasonsData.find(s => s.status === 'active');
        if (activeSeason) {
          setSelectedSeasonId(String(activeSeason.id));
        } else if (seasonsData.length > 0) {
          setSelectedSeasonId(String(seasonsData[0].id));
        }

        // Set first modality as default
        if (modalitiesData.length > 0) {
          setSelectedModalityId('all'); // Start with "All" modalities
        }
      } catch (err) {
        console.error('Failed to load filters:', err);
        setError('Erro ao carregar filtros');
      }
    };

    loadFilters();
  }, []);

  // Fetch tournaments when filters change
  useEffect(() => {
    if (!selectedSeasonId) return;

    const loadTournaments = async () => {
      setLoading(true);
      setError(null);

      try {
        const params: { season_id: number | string; modality_id?: number | string } = {
          season_id: Number(selectedSeasonId),
        };

        // Only add modality_id filter if not "all"
        if (selectedModalityId && selectedModalityId !== 'all') {
          params.modality_id = Number(selectedModalityId);
        }

        const data = await api.tournaments.getTournaments(params);
        setTournaments(data);
      } catch (err) {
        console.error('Failed to load tournaments:', err);
        setError('Erro ao carregar torneios');
      } finally {
        setLoading(false);
      }
    };

    loadTournaments();
  }, [selectedSeasonId, selectedModalityId]);

  // Get display names
  const selectedSeasonDisplayName = seasons.find(s => String(s.id) === String(selectedSeasonId))?.year?.toString() || '';
  const selectedModalityName = selectedModalityId === 'all'
    ? 'Todas as Modalidades'
    : modalities.find(m => String(m.id) === String(selectedModalityId))?.name || '';

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-2 text-gray-800">
            Classificação por Modalidade
          </h1>
          {selectedSeasonDisplayName && selectedModalityName && (
            <p className="text-sm text-gray-600 mb-6">
              {selectedModalityName} - Época: {selectedSeasonDisplayName}
            </p>
          )}

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Época
              </label>
              <select
                value={selectedSeasonId}
                onChange={(e) => setSelectedSeasonId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                disabled={loading || seasons.length === 0}
              >
                {seasons.map((season) => (
                  <option key={season.id} value={season.id}>
                    Época {season.year}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Modalidade
              </label>
              <select
                value={selectedModalityId}
                onChange={(e) => setSelectedModalityId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
                disabled={loading || modalities.length === 0}
              >
                <option value="all">Todas as Modalidades</option>
                {modalities.map((modality) => (
                  <option key={modality.id} value={modality.id}>
                    {modality.name}
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
              <p className="mt-4 text-gray-600">A carregar torneios...</p>
            </div>
          ) : (
            /* Tournament Cards */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {tournaments.length > 0 ? (
                tournaments.map((tournament) => (
                  <TournamentCard
                    key={tournament.id}
                    id={String(tournament.id)}
                    name={tournament.name}
                    modality={tournament.modality.name}
                    epoca={`${tournament.season.year}`}
                    icon="🏆"
                  />
                ))
              ) : (
                <div className="col-span-full text-center py-12">
                  <p className="text-xl text-gray-500">
                    Nenhum torneio encontrado para esta combinação de época e modalidade.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default ClassificacaoModalidade;
