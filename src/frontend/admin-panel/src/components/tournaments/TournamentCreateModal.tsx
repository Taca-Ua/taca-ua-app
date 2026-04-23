import { useState, useEffect } from 'react';
import HelpTooltip from '../HelpTooltip';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentListItem, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type ModalityListItem } from '../../api/modalities';
import Button from '../utils/Button';
import { useModal } from '../../contexts/ModalContext';


const TournamentCreateModal = ({
  onCreate,
  modalityId,
}: {
  onCreate: (tournament: TournamentListItem) => void;
  modalityId?: string;  // Optional prop to fix the modality (e.g., when creating from a modality page)
}) => {
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [modalities, setModalities] = useState<ModalityListItem[]>([]);
  const [loading, setLoading] = useState(false);

  const [name, setName] = useState('');
  const [chosenModality, setChosenModality] = useState<ModalityListItem | null>(null);
  const [isPlayoff, setIsPlayoff] = useState(false);

  // Fetch modalities if needed (only when modality is not fixed)
  useEffect(() => {
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
  }, []);

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
    popModal();
  }

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
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
            <Button
              onClick={onClose}
              type="secondary"
              flexible={true}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleSubmit}
              type="primary"
              flexible={true}
            >
              {loading ? 'A criar...' : 'Criar'}
            </Button>
          </div>
        </div>
      </div>
  );
};

export default TournamentCreateModal;
