import { useState, useEffect } from 'react';
import HelpTooltip from '../HelpTooltip';
import { useNotification } from '../../contexts/NotificationProvider';
<<<<<<< HEAD
import { tournamentsApi, type TournamentListItem, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type ModalityListItem } from '../../api/modalities';
import Button from '../utils/Button';
import { useModal } from '../../contexts/ModalContext';
import ChoseOneInput from '../utils/inputs/ChoseOneInput';
=======
import { tournamentsApi, type Tournament, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { seasonsApi, type Season } from '../../api/seasons';
import { btn } from '../../styles/buttonStyles';
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd


const TournamentCreateModal = ({
  onCreate,
<<<<<<< HEAD
  modalityId,
  starterName,
}: {
  onCreate: (tournament: TournamentListItem) => void;
  modalityId?: string;  // Optional prop to fix the modality (e.g., when creating from a modality page)
  starterName?: string;  // Optional prop to pre-fill the tournament name
}) => {
=======
  fixedModalityId,
  fixedModalityName,
}: TournamentCreateModalProps) => {
  const [name, setName] = useState(fixedModalityName || '');
  const [nameManuallyEdited, setNameManuallyEdited] = useState(!!fixedModalityName);
  const [modalityId, setModalityId] = useState(fixedModalityId || '');
  const [isPlayoff, setIsPlayoff] = useState(false);
  const [loading, setLoading] = useState(false);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [seasonId, setSeasonId] = useState('');
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [modalities, setModalities] = useState<ModalityListItem[]>([]);
  const [loading, setLoading] = useState(false);

  const [name, setName] = useState(starterName || '');
  const [chosenModalityId, setChosenModalityId] = useState<string | null>(null);
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

<<<<<<< HEAD
  const handleSubmit = async () => {
=======
  // Fetch seasons when modal opens
  useEffect(() => {
    if (!isOpen) return;
    const fetchSeasons = async () => {
      try {
        const data = await seasonsApi.getAll();
        setSeasons(data);
        // Pre-select the active season if one exists
        const active = data.find((s) => s.status === 'active');
        if (active) setSeasonId(active.id);
      } catch (err) {
        console.error('Failed to fetch seasons:', err);
      }
    };
    fetchSeasons();
  }, [isOpen]);

  // Auto-fill name when modality changes (only if not manually edited)
  useEffect(() => {
    if (!nameManuallyEdited && modalityId && !isFixedModality) {
      const selected = modalities.find((m) => m.id === modalityId);
      if (selected) setName(selected.name);
    }
  }, [modalityId, modalities, nameManuallyEdited, isFixedModality]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd
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
<<<<<<< HEAD
=======
        competitors: [],
        ...(seasonId ? { season_id: seasonId } : {}),
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd
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
<<<<<<< HEAD
    setChosenModalityId(modalityId || chosenModalityId);
    popModal();
  }
=======
    setSeasonId('');
  };

  if (!isOpen) return null;
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd

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

          {seasons.length > 0 && (
            <div>
              <label className="font-medium">
                Época{' '}
                <HelpTooltip text="Época desportiva a que este torneio pertence. Pré-selecionada com a época ativa, se existir." className="ml-1" />
              </label>
              <select
                value={seasonId}
                onChange={(e) => setSeasonId(e.target.value)}
                className="w-full border border-gray-300 rounded-md p-2"
              >
                <option value="">Sem época</option>
                {seasons.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.year}{s.status === 'active' ? ' (ativa)' : s.status === 'draft' ? ' (rascunho)' : ' (finalizada)'}
                  </option>
                ))}
              </select>
            </div>
          )}

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
