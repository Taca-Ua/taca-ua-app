import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import { btn } from '../../styles/buttonStyles';
import {
  TournamentCreateModal,  TournamentList,
} from '../../components/tournaments';
import ModalityDetailComponent from '../../components/modalities/ModalityDetailComponent';


const TournamentsTab = ({ modalityId, modalityName }: { modalityId: string; modalityName: string }) => {
  const { notify } = useNotification();
  const [tournaments, setTournaments] = useState<TournamentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        setLoading(true);
        const allTournaments = await tournamentsApi.getAll();
        // Filter tournaments by this modality
        const filtered = allTournaments.filter((t) => t.modality.id === modalityId);
        setTournaments(filtered);
      } catch (err) {
        console.error('Failed to fetch tournaments:', err);
        notify('Erro ao carregar torneios', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, [modalityId]);

  const handleCreateTournament = (newTournament: TournamentListItem) => {
    setTournaments([...tournaments, newTournament]);
  };

  const filteredTournaments = tournaments.filter(
    (t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (statusFilter === '' || t.status === statusFilter)
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">Torneios</h2>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className={`px-4 py-2 ${btn.primary} rounded-md`}
        >
          + Criar Torneio
        </button>
      </div>

      <TournamentList
        showModality={false}
        loadTournaments={async () => tournamentsApi.getAll({
          modality_id: modalityId
        })}
        fromModalityId={modalityId}
      />

      <TournamentCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreateTournament}
        fixedModalityId={modalityId}
        fixedModalityName={modalityName}
      />
    </div>
  );
};


function ModalidadeDetail() {
  const modalityId = useParams<{ id: string }>().id;
  if (!modalityId) {
    return <div className="text-red-500">ID de modalidade não fornecido.</div>;
  }

  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'tournaments'>('tournaments');

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8 max-w-5xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes da Modalidade</h1>
          <button
            onClick={() => navigate('/geral/modalidades')}
            className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors`}
          >
            Voltar
          </button>
        </div>

        {/* Modality Information - Always visible at top */}
        <ModalityDetailComponent modalityId={modalityId} />

        {/* Tab System */}
        <div className="bg-white rounded-lg shadow-md">
          {/* Tab Headers */}
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('tournaments')}
                className={`px-6 py-4 font-medium transition-colors border-b-2 ${
                  activeTab === 'tournaments'
                    ? 'border-teal-500 text-teal-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Torneios
              </button>
              {/* Future tabs can be added here */}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'tournaments' && (
              <TournamentsTab modalityId={modalityId} modalityName={""} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ModalidadeDetail;
