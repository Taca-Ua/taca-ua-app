import { useState, useEffect } from 'react';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type Tournament } from '../../api/tournaments';
import { btn } from '../../styles/buttonStyles';
import {
  TournamentCreateModal,
  TournamentFilters,
  TournamentList,
} from '../../components/tournaments';

const Torneios = () => {
  const [loading, setLoading] = useState(true);
  const { notify: notifyPage } = useNotification();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [modalityFilter, setModalityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Fetch tournaments on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const tournamentsData = await tournamentsApi.getAll();
        setTournaments(tournamentsData);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        notifyPage('Erro ao carregar dados', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter tournaments based on search and filters
  const filteredTournaments = tournaments.filter(
    (t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (modalityFilter === '' || t.modality.id === modalityFilter) &&
      (statusFilter === '' || t.status === statusFilter)
  );

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Torneios</h1>

          <button
            onClick={() => setIsModalOpen(true)}
            className={`px-6 py-3 ${btn.primary} rounded-md`}
          >
            + Criar Torneio
          </button>
        </div>

        <TournamentFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          modalityFilter={modalityFilter}
          onModalityChange={setModalityFilter}
          statusFilter={statusFilter}
          onStatusChange={setStatusFilter}
          availableTournaments={tournaments}
          showModalityFilter={true}
        />

        <div className="bg-white shadow-md rounded-lg p-6 mt-6">
          <TournamentList
            tournaments={filteredTournaments}
            loading={loading}
            showModality={true}
            emptyMessage={
              searchQuery || modalityFilter || statusFilter
                ? 'Nenhum torneio encontrado com os filtros aplicados.'
                : 'Nenhum torneio encontrado.'
            }
          />
        </div>

        <TournamentCreateModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onCreate={(newTournament) => setTournaments([...tournaments, newTournament])}
        />
      </div>
    </div>
  );
};

export default Torneios;
