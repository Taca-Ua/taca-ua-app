import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import { tournamentsApi, type TournamentDetail } from '../../api';

function Tournaments() {
  const [tournaments, setTournaments] = useState<TournamentDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          page,
          page_size: 20,
          ...(statusFilter !== 'all' && { status: statusFilter }),
        };

        const data = await tournamentsApi.getAll(params);
        setTournaments(data.items);
        setTotalPages(Math.ceil(data.total / data.page_size));
      } catch (err) {
        console.error('Error fetching tournaments:', err);
        setError('Erro ao carregar torneios. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, [page, statusFilter]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-PT', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-green-100 text-green-800',
      finished: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800',
    };

    const statusLabels = {
      draft: 'Rascunho',
      active: 'Ativo',
      finished: 'Finalizado',
      cancelled: 'Cancelado',
    };

    const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
    const label = statusLabels[status as keyof typeof statusLabels] || status;

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
        {label}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Torneios
            </h1>
            <p className="text-lg text-gray-600">
              Veja todos os torneios e classificações
            </p>
          </div>

          {/* Filters */}
          <div className="mb-6 flex gap-4 flex-wrap">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="all">Todos os Estados</option>
              <option value="draft">Rascunho</option>
              <option value="active">Ativo</option>
              <option value="finished">Finalizado</option>
              <option value="cancelled">Cancelado</option>
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
              <p className="mt-4 text-gray-600">A carregar torneios...</p>
            </div>
          ) : (
            <>
              {/* Tournaments Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tournaments.length === 0 ? (
                  <div className="col-span-full bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">Não há torneios disponíveis com os filtros selecionados.</p>
                  </div>
                ) : (
                  tournaments.map((tournament) => (
                    <Link
                      key={tournament.tournament_id}
                      to={`/torneios/${tournament.tournament_id}`}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 flex flex-col"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-semibold text-gray-800 flex-1">
                          {tournament.tournament_name}
                        </h3>
                        {getStatusBadge(tournament.status)}
                      </div>

                      <div className="space-y-2 mb-4 flex-grow">
                        <div>
                          <p className="text-sm text-gray-500">Modalidade</p>
                          <p className="font-medium text-gray-700">
                            {tournament.modality_name || tournament.modality_type_name}
                          </p>
                        </div>

                        <div>
                          <p className="text-sm text-gray-500">Data de Início</p>
                          <p className="font-medium text-gray-700">
                            {formatDate(tournament.start_date)}
                          </p>
                        </div>
                      </div>

                      <div className="border-t pt-4 grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Competidores</p>
                          <p className="text-lg font-semibold text-teal-600">
                            {tournament.competitor_count}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Jogos</p>
                          <p className="text-lg font-semibold text-teal-600">
                            {tournament.match_count}
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

export default Tournaments;
