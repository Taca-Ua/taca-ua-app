import { useState } from 'react';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import { btn } from '../../styles/buttonStyles';
import TournamentCreateModal from '../../components/tournaments/TournamentCreateModal';
import TournamentList from '../../components/tournaments/TournamentList';

const Torneios = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tournaments, setTournaments] = useState<TournamentListItem[]>([]);


  return (
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

        <div className="bg-white shadow-md rounded-lg p-6 mt-6">
          <TournamentList
            tournamentsState={[tournaments, setTournaments]}
            showModality={true}
            loadTournaments={async () => tournamentsApi.getAll()}
          />
        </div>

        <TournamentCreateModal
          controller={[isModalOpen, setIsModalOpen]}
          onCreate={(newTournament) => setTournaments([...tournaments, newTournament])}
        />
      </div>
  );
};

export default Torneios;
