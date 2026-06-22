import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchesApi, type MatchListItem } from '../../api/matches';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';
import MatchesCalendarComponent from '../../components/matches/MatchesCalendarComponent';

const Jogos = () => {
  const navigate = useNavigate();
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [tournamentMap, setTournamentMap] = useState<Record<string, TournamentListItem>>({});
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('calendar');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalMatches, setTotalMatches] = useState(0);
  const itemsPerPage = 10;

  // Fetch matches and tournaments from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const query = statusFilter === 'all' ? {} : { status: statusFilter };
        const [fetchedMatches, fetchedTournaments] = await Promise.all([
          matchesApi.getAll({ page: currentPage, limit: itemsPerPage, ...query }),
          tournamentsApi.getAll(),
        ]);
        setMatches(fetchedMatches.matches);
        setTotalMatches(fetchedMatches.total);
        const map: Record<string, TournamentListItem> = {};
        fetchedTournaments.forEach(t => { map[t.id] = t; });
        setTournamentMap(map);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        notify('Não foi possível carregar os jogos do núcleo. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentPage, statusFilter]);

  // Helper function to format match date/time
  const formatDateTime = (startTime: string) => {
    const date = new Date(startTime);
    return {
      date: date.toLocaleDateString('pt-PT'),
      time: date.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  // Helper function to get status display
  const getStatusDisplay = (status: string) => {
    const statusMap: Record<string, string> = {
      scheduled: 'Agendado',
      in_progress: 'Em curso',
      finished: 'Terminado',
      canceled: 'Cancelado',
    };
    return statusMap[status] || status;
  };

  // Pagination calculations
  const totalPages = Math.ceil(totalMatches / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage + 1;
  const endIndex = Math.min(currentPage * itemsPerPage, totalMatches);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-800">Jogos</h1>

            <div className="flex flex-wrap gap-2 items-center">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="all">Todos os estados</option>
                <option value="scheduled">Agendado</option>
                <option value="in_progress">Em curso</option>
                <option value="finished">Terminado</option>
                <option value="canceled">Cancelado</option>
              </select>

              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    viewMode === 'list'
                      ? 'bg-teal-500 text-white'
                      : btn.secondaryAlt
                  }`}
                >
                  Lista
                </button>
                <button
                  onClick={() => setViewMode('calendar')}
                  className={`px-4 py-2 rounded-md font-medium transition-colors ${
                    viewMode === 'calendar'
                      ? 'bg-teal-500 text-white'
                      : btn.secondaryAlt
                  }`}
                >
                  Calendário
                </button>
              </div>
            </div>
          </div>

          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {!loading && (
            <>
              {viewMode === 'list' && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="space-y-3">
                    {matches.length > 0 ? (
                      matches.map((match) => {
                        const { date, time } = formatDateTime(match.start_time);
                        const tournament = tournamentMap[match.tournament.id];
                        return (
                          <button
                            key={match.id}
                            type="button"
                            onClick={() => navigate(`/jogos/${match.id}`)}
                            className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <span className="text-gray-800 font-bold text-lg">
                                {match.participants.map(p => p.name || 'TBD').join(' vs ')}
                              </span>
                              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                                match.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                                match.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
                                match.status === 'finished' ? 'bg-green-100 text-green-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {getStatusDisplay(match.status)}
                              </span>
                            </div>
                            {tournament && (
                              <div className="flex gap-2 mb-2 text-sm">
                                <span className="text-teal-600 font-medium">{tournament.name}</span>
                                {tournament.modality && (
                                  <>
                                    <span className="text-gray-400">·</span>
                                    <span className="text-gray-500">{tournament.modality.name}</span>
                                  </>
                                )}
                              </div>
                            )}
                            <div className="flex gap-6 text-sm text-gray-600">
                              <span>
                                <span className="font-medium">Data:</span> {date}
                              </span>
                              <span>
                                <span className="font-medium">Hora:</span> {time}
                              </span>
                              <span>
                                <span className="font-medium">Local:</span> {match.location}
                              </span>
                            </div>
                          </button>
                        );
                      })
                    ) : (
                      <p className="text-gray-500 text-center py-8">
                        Nenhum jogo encontrado.
                      </p>
                    )}
                  </div>

                  {/* Pagination Controls */}
                  {totalMatches > itemsPerPage && (
                    <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                      <div className="text-sm text-gray-600">
                        Mostrando <span className="font-medium">{startIndex}</span> até{' '}
                        <span className="font-medium">{endIndex}</span> de{' '}
                        <span className="font-medium">{totalMatches}</span> jogos
                      </div>

                      <div className="flex gap-2 items-center flex-wrap justify-center">
                        <button
                          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                          disabled={currentPage === 1}
                          className="px-4 py-2 rounded-md font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed bg-gray-200 text-gray-800 hover:bg-gray-300 transition-colors"
                        >
                          Anterior
                        </button>

                        {(() => {
                          const pageNumbers = [];
                          const maxPagesToShow = 5;
                          let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
                          let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

                          if (endPage - startPage + 1 < maxPagesToShow) {
                            startPage = Math.max(1, endPage - maxPagesToShow + 1);
                          }

                          if (startPage > 1) {
                            pageNumbers.push(
                              <button
                                key={1}
                                onClick={() => setCurrentPage(1)}
                                className="px-3 py-2 rounded-md text-sm font-medium bg-gray-200 text-gray-800 hover:bg-gray-300 transition-colors"
                              >
                                1
                              </button>
                            );
                            if (startPage > 2) {
                              pageNumbers.push(
                                <span key="ellipsis-start" className="px-2 py-2 text-gray-600">
                                  ...
                                </span>
                              );
                            }
                          }

                          for (let i = startPage; i <= endPage; i++) {
                            pageNumbers.push(
                              <button
                                key={i}
                                onClick={() => setCurrentPage(i)}
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                  currentPage === i
                                    ? 'bg-teal-500 text-white'
                                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                                }`}
                              >
                                {i}
                              </button>
                            );
                          }

                          if (endPage < totalPages) {
                            if (endPage < totalPages - 1) {
                              pageNumbers.push(
                                <span key="ellipsis-end" className="px-2 py-2 text-gray-600">
                                  ...
                                </span>
                              );
                            }
                            pageNumbers.push(
                              <button
                                key={totalPages}
                                onClick={() => setCurrentPage(totalPages)}
                                className="px-3 py-2 rounded-md text-sm font-medium bg-gray-200 text-gray-800 hover:bg-gray-300 transition-colors"
                              >
                                {totalPages}
                              </button>
                            );
                          }

                          return pageNumbers;
                        })()}

                        <button
                          onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                          disabled={currentPage === totalPages}
                          className="px-4 py-2 rounded-md font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed bg-gray-200 text-gray-800 hover:bg-gray-300 transition-colors"
                        >
                          Próxima
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {viewMode === 'calendar' && (
                <MatchesCalendarComponent />
              )}
            </>
          )}
        </div>
      </div>
  );
};

export default Jogos;
