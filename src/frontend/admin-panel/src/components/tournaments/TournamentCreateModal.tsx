import { useState } from 'react';
import HelpTooltip from '../HelpTooltip';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentListItem, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi } from '../../api/modalities';
import Button from '../utils/Button';
import { useModal } from '../../contexts/ModalContext';
import ChoseOneInput from '../utils/inputs/ChoseOneInput';


const TournamentCreateModal = ({
  onCreate,
  modalityId,
  starterName,
}: {
  onCreate: (tournament: TournamentListItem) => void;
  modalityId?: string;  // Optional prop to fix the modality (e.g., when creating from a modality page)
  starterName?: string;  // Optional prop to pre-fill the tournament name
}) => {
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [loading, setLoading] = useState(false);

  const [name, setName] = useState(starterName || '');
  const [chosenModalityId, setChosenModalityId] = useState<string | null>(null);
  const [isPlayoff, setIsPlayoff] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    if (name.trim() === '') {
      notify('O nome do torneio é obrigatório.', 'error');
      setLoading(false);
      return;
    }

    let modalityIdToUse = chosenModalityId ? chosenModalityId : modalityId;

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
    setChosenModalityId(modalityId || chosenModalityId);
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
            <ChoseOneInput
              allElementsLoader={() => modalitiesApi.getAll().then(res => res.map(c => ({ id: c.id, title: c.name })))}
              onSelect={(ele) => setChosenModalityId(ele ? ele.id : null)}
            />
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
