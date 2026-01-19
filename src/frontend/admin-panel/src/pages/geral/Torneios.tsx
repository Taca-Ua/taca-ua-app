import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { tournamentsApi, type Tournament, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { teamsApi, type Team } from '../../api/teams';


const TorneiosCreateModal = ({ isOpen, onClose, onCreate, modalities, setModalities }: {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (tournament: Tournament) => void;
  modalities: Modality[];
  setModalities: React.Dispatch<React.SetStateAction<Modality[]>>;
}) => {
  const [name, setName] = useState('');
  const [modalityId, setModalityId] = useState('');
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeams, setSelectedTeams] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch modalities on first mount if not already loaded
  useEffect(() => {
    const fetchModalities = async () => {
      try {
        const modalitiesData = await modalitiesApi.getAll();
        setModalities(modalitiesData);
      }
      catch (err) {
        console.error('Failed to fetch modalities:', err);
      }
    };

    if (modalities.length === 0) {
      fetchModalities();
    }
  }, []);

  // Fetch teams when selected modality changes
  useEffect(() => {
    setSelectedTeams([]); // Reset selected teams when modality changes
    const fetchTeamsByModality = async () => {
      if (!modalityId) return;
      try {
        const allTeams = await teamsApi.getAll(modalityId);
        setTeams(allTeams);
      }
      catch (err) {
        console.error('Failed to fetch teams by modality:', err);
      }
    };
    fetchTeamsByModality();
  }, [modalityId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const newTournament: TournamentCreate = {
        name,
        modality_id: modalityId,
        competitors: selectedTeams.map(teamId => ({ competitor_type: 'team', team_id: teamId })),
      };
      const createdTournament = await tournamentsApi.create(newTournament);
      onCreate(createdTournament);
      onClose();
    } catch (err) {
      console.error('Failed to create tournament:', err);
      setError('Erro ao criar torneio');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-8 rounded-lg w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4">Criar Torneio</h2>
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name of the tournament */}
          <div>
            <label className="font-medium">Nome do Torneio <span className="text-red-500">*</span></label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2"
              required
            />
          </div>

          {/* Modality of the tournament */}
          <div>
            <label className="font-medium">Modalidade <span className="text-red-500">*</span></label>
            <select
              value={modalityId}
              onChange={(e) => setModalityId(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2"
              required
            >
              <option value="" disabled>Selecione uma modalidade</option>
              {modalities.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>

          {/* Teams selection */}
          <div>
            <label className="font-medium">Equipas</label>
            <select
              multiple
              value={selectedTeams}
              onChange={(e) => {
                const options = e.target.options;
                const selected: string[] = [];
                for (let i = 0; i < options.length; i++) {
                  if (options[i].selected) {
                    selected.push(options[i].value);
                  }
                }
                setSelectedTeams(selected);
              }}
              className="w-full border border-gray-300 rounded-md p-2 h-32"
            >
              {teams.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 rounded-md"
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-teal-500 text-white rounded-md"
              disabled={loading}
            >
              {loading ? 'A criar...' : 'Criar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const Torneios = () => {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);  // lazy load modalities

  // Fetch tournaments on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [tournamentsData] = await Promise.all([
          tournamentsApi.getAll(),
        ]);
        setTournaments(tournamentsData);
        setError('');
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Erro ao carregar dados');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Torneios</h1>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md"
          >
            + Criar Torneio
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {/* Lista */}
        <div className="bg-white shadow-md rounded-lg p-6 space-y-3">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : tournaments.length > 0 ? (
            tournaments.map(t => (
              <div
                key={t.id}
                onClick={() => navigate(`/geral/torneios/${t.id}`)}
                className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer flex justify-between"
              >
                <div className="font-medium">{t.name}</div>
                <div className="text-sm text-teal-600">
                  {t.modality_name} {t.status}
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center">Nenhum torneio encontrado.</p>
          )}
        </div>

        {/* Create Modal */}
        {isModalOpen &&
          <TorneiosCreateModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onCreate={(newTournament) => setTournaments([...tournaments, newTournament])}
            modalities={modalities}
            setModalities={setModalities}
          />
        }

      </div>

    </div>
  );
};

export default Torneios;
