import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import TournamentList from '../../components/tournaments/TournamentList';
import TournamentCreateModal from '../../components/tournaments/TournamentCreateModal';
import ModalityDetailComponent from '../../components/modalities/ModalityDetailComponent';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import { useAuth } from '../../hooks/useAuth';


const TournamentsTab = ({ modalityId }: { modalityId: string }) => {
  const [tournaments, setTournaments] = useState<TournamentListItem[]>([]);
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();

  const handleCreateTournament = (newTournament: TournamentListItem) => {
    setTournaments([...tournaments, newTournament]);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">Torneios</h2>
        <Button
          onClick={() => pushModal(
            <TournamentCreateModal
              onCreate={handleCreateTournament}
              modalityId={modalityId}
            />
          )}
          type='primary'
          padding='px-4 py-2'
          active={isAdminGeneral}
        >
          + Criar Torneio
        </Button>
      </div>

      <TournamentList
        tournamentsState={[tournaments, setTournaments]}
        showModality={false}
        loadTournaments={async () => tournamentsApi.getAll({
          modality_id: modalityId
        })}
        fromModalityId={modalityId}
        showModalityFilter={false}
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
      <div className="flex-1 p-8 max-w-5xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes da Modalidade</h1>
          <Button
            onClick={() => navigate('/modalidades')}
            type='secondary'
            padding='px-6 py-3'
          >
            Voltar
          </Button>
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
              <TournamentsTab modalityId={modalityId} />
            )}
          </div>
        </div>
      </div>
  );
}

export default ModalidadeDetail;
