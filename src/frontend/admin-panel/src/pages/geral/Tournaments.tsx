import { useState } from 'react';
import { type TournamentListItem } from '../../api/tournaments';
import TournamentCreateModal from '../../components/tournaments/TournamentCreateModal';
import TournamentList from '../../components/tournaments/TournamentList';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import SeasonSelector from '../../components/seasons/SeasonSelector';

const Torneios = () => {
  const { isAdminGeneral } = useAuth();
  const [tournaments, setTournaments] = useState<TournamentListItem[] | null>(null);
  const { pushModal } = useModal();

  return (
    <>
      <SeasonSelector />
      <div className="flex-1 p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Torneios</h1>
          <Button
            onClick={() => pushModal(
              <TournamentCreateModal
                onCreate={(newTournament) => setTournaments(prev => prev ? [...prev, newTournament] : [newTournament])}
              />
            )}
            type='primary'
            padding='px-6 py-3'
            active={isAdminGeneral}
          >
            + Criar Torneio
          </Button>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6 mt-6">
          <TournamentList
            tournamentsState={[tournaments, setTournaments]}
          />
        </div>
      </div>
    </>
  );
};

export default Torneios;
