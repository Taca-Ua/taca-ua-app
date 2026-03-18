import { useState, useEffect } from 'react';
import HelpTooltip from '../../components/HelpTooltip';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type Tournament, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { btn } from '../../styles/buttonStyles';


const TorneiosCreateModal = ({ isOpen, onClose, onCreate, modalities, setModalities }: {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (tournament: Tournament) => void;
  modalities: Modality[];
  setModalities: React.Dispatch<React.SetStateAction<Modality[]>>;
}) => {
  const [name, setName] = useState('');
  const [modalityId, setModalityId] = useState('');
  const [isPlayoff, setIsPlayoff] = useState(false);
  const [loading, setLoading] = useState(false);
  const { notify } = useNotification();

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newTournament: TournamentCreate = {
        name,
        modality_id: modalityId,
        is_playoff: isPlayoff,
        competitors: [],
      };
      const createdTournament = await tournamentsApi.create(newTournament);
      onCreate(createdTournament);
      onClose();
    } catch (err) {
      console.error('Failed to create tournament:', err);
      notify('Não foi possível criar o torneio. Verifique os dados e tente novamente.', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-8 rounded-lg w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4">Criar Torneio</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="font-medium">Nome do Torneio <HelpTooltip text="Nome identificador do torneio para a época atual. Deve ser descritivo e único para facilitar a identificação." className="ml-1" /> <span className="text-red-500">*</span></label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2"
              required
            />
          </div>

          <div>
            <label className="font-medium">Modalidade <HelpTooltip text="Desporto ou atividade para o qual este torneio é organizado. A modalidade determina as regras de inscrição (equipas vs atletas)." className="ml-1" /> <span className="text-red-500">*</span></label>
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

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_playoff_create"
              checked={isPlayoff}
              onChange={(e) => setIsPlayoff(e.target.checked)}
              className="w-4 h-4 accent-teal-500"
            />
            <label htmlFor="is_playoff_create" className="font-medium cursor-pointer">
              Torneio de Playoff
            </label>
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
  const { notify: notifyPage } = useNotification();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);  // lazy load modalities
  const [searchQuery, setSearchQuery] = useState('');
  const [modalityFilter, setModalityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Fetch tournaments on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [tournamentsData] = await Promise.all([
          tournamentsApi.getAll(),
        ]);
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

        <div className="flex gap-3 mb-6">
          <input
            type="text"
            placeholder="Pesquisar torneio..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
          <select
            value={modalityFilter}
            onChange={(e) => setModalityFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
          >
            <option value="">Todas as modalidades</option>
            {[...new Map(tournaments.map(t => [t.modality.id, t.modality])).values()]
              .sort((a, b) => a.name.localeCompare(b.name))
              .map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
          >
            <option value="">Todos os estados</option>
            <option value="draft">Rascunho</option>
            <option value="active">Ativo</option>
            <option value="finished">Finalizado</option>
          </select>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6 space-y-3">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : tournaments.filter(t =>
              t.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
              (modalityFilter === '' || t.modality.id === modalityFilter) &&
              (statusFilter === '' || t.status === statusFilter)
            ).length > 0 ? (
            tournaments
              .filter(t =>
                t.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
                (modalityFilter === '' || t.modality.id === modalityFilter) &&
                (statusFilter === '' || t.status === statusFilter)
              )
              .map(t => (
              <button
                key={t.id}
                type="button"
                onClick={() => navigate(`/geral/torneios/${t.id}`)}
                className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 flex justify-between items-center focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <div className="flex flex-col">
                  <span className="font-medium text-gray-800">{t.name}</span>

                  <span className="text-xs text-gray-500 mt-1">
                    {t.start_date
                      ? `Início: ${new Date(t.start_date).toLocaleDateString('pt-PT')}`
                      : 'Data não definida'}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <span className="text-teal-600 font-medium">{t.modality.name}</span>
                  <span className="text-gray-400">|</span>
                  <span className={`px-2 py-1 rounded-full font-medium ${
                    t.status === 'active' ? 'bg-green-100 text-green-800' :
                    t.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                    t.status === 'finished' ? 'bg-gray-100 text-gray-600' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {t.status === 'active' ? 'Ativo' : t.status === 'draft' ? 'Rascunho' : t.status === 'finished' ? 'Finalizado' : t.status}
                  </span>
                </div>
              </button>
            ))
          ) : (
            <p className="text-gray-500 text-center">Nenhum torneio encontrado.</p>
          )}
        </div>

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
