import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { nucleosApi, teamsApi, type NucleoPublic, type TeamDetail } from '../api';

function NucleoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [nucleo, setNucleo] = useState<NucleoPublic | null>(null);
  const [teams, setTeams] = useState<TeamDetail[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load nucleo info once
  useEffect(() => {
    if (!id) return;
    nucleosApi.getById(id).then(setNucleo).catch(() => setError('Núcleo não encontrado.'));
  }, [id]);

  // Load all teams for this nucleo at once
  useEffect(() => {
    if (!id) return;
    const loadTeams = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await teamsApi.getAll({ nucleo_id: id, page: 1, page_size: 100 });
        setTeams(data.items);
      } catch (err) {
        console.error('Error fetching teams:', err);
        setError('Erro ao carregar equipas.');
      } finally {
        setLoading(false);
      }
    };
    loadTeams();
  }, [id]);

  const filtered = teams.filter((t) =>
    t.team_name.toLowerCase().includes(search.toLowerCase()) ||
    (t.modality_name ?? t.modality_type_name).toLowerCase().includes(search.toLowerCase()) ||
    t.course_abbreviation.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2 text-sm text-gray-500">
            <Link to="/nucleos" className="hover:text-teal-600">
              Núcleos
            </Link>
            <span>/</span>
            <span className="text-gray-700">{nucleo?.name ?? 'Detalhe'}</span>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Nucleo header */}
          {nucleo && (
            <div className="bg-white rounded-lg shadow p-6 mb-8 flex items-center gap-5">
              <div className="w-16 h-16 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0 overflow-hidden">
                {nucleo.logo_url ? (
                  <img
                    src={nucleo.logo_url}
                    alt={nucleo.abbreviation}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-teal-700 font-bold text-xl">{nucleo.abbreviation}</span>
                )}
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-gray-800">{nucleo.name}</h1>
                <p className="text-gray-500 mt-1">{nucleo.abbreviation}</p>
              </div>
            </div>
          )}

          {/* Teams section */}
          <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
            <h2 className="text-xl font-semibold text-gray-800">
              Equipas {!loading && `(${filtered.length})`}
            </h2>
            <input
              type="text"
              placeholder="Pesquisar equipa..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent w-full sm:w-64"
            />
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar equipas...</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filtered.length === 0 ? (
                  <div className="col-span-full bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">Nenhuma equipa encontrada.</p>
                  </div>
                ) : (
                  filtered.map((team) => (
                    <Link
                      key={team.team_id}
                      to={`/equipas/${team.team_id}`}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 flex flex-col text-inherit"
                    >
                      <div className="mb-3">
                        <h3 className="text-lg font-semibold text-gray-800 mb-1">
                          {team.team_name}
                        </h3>
                        <p className="text-sm text-teal-600 font-medium">
                          {team.modality_name || team.modality_type_name}
                        </p>
                      </div>
                      <div className="mt-auto border-t pt-3 flex justify-between items-center">
                        <p className="text-sm text-gray-500">{team.course_abbreviation}</p>
                        <p className="text-sm font-semibold text-gray-700">
                          {team.player_count} jogador{team.player_count !== 1 ? 'es' : ''}
                        </p>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </>
          )}

          <div className="mt-8">
            <Link to="/nucleos" className="text-teal-600 hover:text-teal-700 text-sm font-medium">
              ← Voltar aos Núcleos
            </Link>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default NucleoDetailPage;
