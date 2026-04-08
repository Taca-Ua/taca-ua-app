import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { nucleosApi, type NucleoPublic } from '../api';

function Nucleos() {
  const [nucleos, setNucleos] = useState<NucleoPublic[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await nucleosApi.getAll({ page: 1, page_size: 100 });
        setNucleos(data.items);
      } catch (err) {
        console.error('Error fetching nucleos:', err);
        setError('Erro ao carregar núcleos. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const filtered = nucleos.filter((n) =>
    n.name.toLowerCase().includes(search.toLowerCase()) ||
    n.abbreviation.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">Núcleos</h1>
            <p className="text-lg text-gray-600">
              Conheça os núcleos participantes da Taça UA
            </p>
          </div>

          {/* Search */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Pesquisar núcleo..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar núcleos...</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {filtered.length === 0 ? (
                  <div className="col-span-full bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">Nenhum núcleo encontrado.</p>
                  </div>
                ) : (
                  filtered.map((nucleo) => (
                    <Link
                      key={nucleo.nucleo_id}
                      to={`/nucleos/${nucleo.nucleo_id}`}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 flex items-center gap-4 text-inherit"
                    >
                      <div className="w-14 h-14 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0 overflow-hidden">
                        {nucleo.logo_url ? (
                          <img
                            src={nucleo.logo_url}
                            alt={nucleo.abbreviation}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <span className="text-teal-700 font-bold text-lg">
                            {nucleo.abbreviation}
                          </span>
                        )}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">{nucleo.name}</h3>
                        <p className="text-sm text-gray-500">{nucleo.abbreviation}</p>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default Nucleos;
