import { useState, useEffect } from 'react';
import HelpTooltip from '../HelpTooltip';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentListItem, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type ModalityListItem } from '../../api/modalities';
import { btn } from '../../styles/buttonStyles';


const TournamentCreateModal = ({
  controller,
  onCreate,
  modalityId,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onCreate: (tournament: TournamentListItem) => void;
  modalityId?: string;
}) => {
  const { notify } = useNotification();

  const [isOpen, setIsOpen] = controller;
  const [modalities, setModalities] = useState<ModalityListItem[]>([]);
  const [loading, setLoading] = useState(false);

  const [name, setName] = useState('');
  const [chosenModality, setChosenModality] = useState<ModalityListItem | null>(null);
  const [isPlayoff, setIsPlayoff] = useState(false);

  // Fetch modalities if needed (only when modality is not fixed)
  useEffect(() => {
    if (!isOpen) return;  // Only fetch when modal is opened
    if (modalityId) return;  // No need to fetch if modality is fixed

    const fetchModalities = async () => {
      try {
        const modalitiesData = await modalitiesApi.getAll();
        setModalities(modalitiesData);
      } catch (err) {
        console.error('Failed to fetch modalities:', err);
      }
    };

    if (modalities.length === 0) {
      fetchModalities();
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    setLoading(true);
    if (name.trim() === '') {
      notify('O nome do torneio é obrigatório.', 'error');
      setLoading(false);
      return;
    }

    let modalityIdToUse = chosenModality ? chosenModality.id : modalityId;

    if (!modalityIdToUse) {
      notify('Por favor, selecione uma modalidade.', 'error');
      setLoading(false);
      return;
    }

    try {
      const newTournament: TournamentCreate = {
        name,
        modality_id: modalityIdToUse,
        is_playoff: isPlayoff,
      };
      console.log('Creating tournament with data:', newTournament);
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

  const onClose = () => {
    setName('');
    setIsPlayoff(false);
    setChosenModality(null);
    setIsOpen(false);
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-8 rounded-lg w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4">Criar Torneio</h2>

        <div className="space-y-4">
          <div>
            <label className="font-medium">
              Nome do Torneio{' '}
              <HelpTooltip
                text="Nome identificador do torneio para a época atual. Deve ser descritivo e único para facilitar a identificação."
                className="ml-1"
              />{' '}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2"
              required
            />
          </div>

          {/* Modalidade */}
          {modalityId ? null : (
            <div>
              <label className="font-medium">
                Modalidade{' '}
                <HelpTooltip
                  text="Desporto ou atividade para o qual este torneio é organizado. A modalidade determina as regras de inscrição (equipas vs atletas)."
                  className="ml-1"
              />
              <span className="text-red-500">*</span>
            </label>
            <select
              value={chosenModality?.id || ''}
              onChange={(e) => setChosenModality(modalities.find((m) => m.id === e.target.value) || null)}
              className="w-full border border-gray-300 rounded-md p-2"
              required
            >
              <option value="" disabled>
                Selecione uma modalidade
              </option>
              {[...modalities].sort((a, b) => a.name.localeCompare(b.name)).map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>)}

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
              className={`px-4 py-2 ${btn.secondary} rounded-md`}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              className={`px-4 py-2 ${btn.primary} rounded-md`}
              disabled={loading}
            >
              {loading ? 'A criar...' : 'Criar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TournamentCreateModal;
