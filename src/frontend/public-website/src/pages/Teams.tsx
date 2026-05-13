import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { teamsApi, type TeamDetail } from '../api';
import { type SeasonDetail, seasonsApi } from '../api/seasons';

function Teams() {
  const [teams, setTeams] = useState<TeamDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [seasons, setSeasons] = useState<SeasonDetail[]>([]);
  const [seasonFilter, setSeasonFilter] = useState<number>(1); // Default season ID

  useEffect(() => {
    seasonsApi
      .getAll()
      .then((data) => {
        setSeasons(data.items);
        if (data.items.length > 0) {
          setSeasonFilter(data.items[0].season_id); // Set default season filter to the first season
        }
      })
      .catch((err) => {
        console.error('Error fetching seasons:', err);
        setError('Erro ao carregar épocas. Por favor, tente novamente.');
      });
  }, []);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          page,
          page_size: 20,
          season_id: seasonFilter, // Filter teams by selected season
        };

        const data = await teamsApi.getAll(params);
        setTeams(data.items);
        setTotalPages(Math.ceil(data.total / data.page_size));
      } catch (err) {
        console.error('Error fetching teams:', err);
        setError('Erro ao carregar equipas. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, [page, seasonFilter]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Equipas
            </h1>
            <p className="text-lg text-gray-600">
              Veja todas as equipas participantes da Taça UA
            </p>
          </div>

          <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <select
              id="season-filter"
              value={seasonFilter}
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
              <p className="mt-4 text-gray-600">A carregar equipas...</p>
            </div>
          ) : (
            <>
              {/* Teams Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {teams.length === 0 ? (
                  <div className="col-span-full bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">Não há equipas disponíveis.</p>
                  </div>
                ) : (
                  teams.map((team) => (
                    <Link
                      key={team.team_id}
                      to={`/equipas/${team.team_id}`}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 flex flex-col text-inherit"
                    >
                      <div className="mb-4">
                        <h3 className="text-xl font-semibold text-gray-800 mb-2">
                          {team.team_name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {team.modality_name || team.modality_type_name}
                        </p>
                      </div>

                      <div className="space-y-3 mb-4">
                        <div>
                          <p className="text-sm text-gray-500">Curso</p>
                          <p className="font-medium text-gray-700">{team.course_name}</p>
                          <p className="text-xs text-gray-500">{team.course_abbreviation}</p>
                        </div>

                        <div>
                          <p className="text-sm text-gray-500">Núcleo</p>
                          <p className="font-medium text-gray-700">{team.nucleo_name}</p>
                          <p className="text-xs text-gray-500">{team.nucleo_abbreviation}</p>
                        </div>
                      </div>

                      <div className="border-t pt-4">
                        <div className="flex justify-between items-center">
                          <p className="text-sm text-gray-500">Jogadores</p>
                          <p className="text-2xl font-semibold text-teal-600">
                            {team.player_count}
                          </p>
                        </div>
                      </div>
                    </Link>
                  ))
                )}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex justify-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <span className="px-4 py-2 text-gray-700">
                    Página {page} de {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Próxima
                  </button>
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

export default Teams;
