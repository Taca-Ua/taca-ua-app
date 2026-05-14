import { useEffect, useState } from 'react';
import HelpTooltip from '../HelpTooltip';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentListItem, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type ModalityListItem } from '../../api/modalities';
import Button from '../utils/Button';
import { useModal } from '../../contexts/ModalContext';
import ChoseOneInput from '../utils/inputs/ChoseOneInput';
import { useSeason } from '../../contexts/SeasonContext';
import { modalityTypesApi } from '../../api/modality-types';


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
  const { loadedSeason } = useSeason();

  const [loading, setLoading] = useState(false);

  const [name, setName] = useState(starterName || '');
  const [chosenModalityId, setChosenModalityId] = useState<string | null>(modalityId || null);
  const [chosenScoringFormat, setChosenScoringFormat] = useState<{ id: string, title: string } | null>(null);

  const [modalityOptions, setModalityOptions] = useState<ModalityListItem[]>([]);

  const fetchModalities = async () => {
    return (await modalitiesApi.getAll({ season_id: loadedSeason?.id })).filter(c => c.belongs_to_season);
  };

  useEffect(() => {
    fetchModalities().then(res => {
      const options = res.filter(c => c.belongs_to_season);
      setModalityOptions(options);
      if (chosenModalityId) {
        const foundModality = options.find(m => m.id === chosenModalityId);
        if (!foundModality) {
          setChosenModalityId(null);
          notify('A modalidade selecionada não pertence à época atual. Por favor, selecione outra modalidade.', 'error');
        } else {
          let modalityType = options.find(m => m.id === chosenModalityId)?.modality_type;
          setChosenScoringFormat(modalityType ? { id: modalityType.id, title: modalityType.name } : null);
        }
      } else if (options.length === 1) {
        setChosenModalityId(options[0].id);
        let modalityType = options[0].modality_type;
        setChosenScoringFormat(modalityType ? { id: modalityType.id, title: modalityType.name } : null);
        if (!name) setName(options[0].name);
      }
    }).catch(err => {
      console.error('Failed to load modalities:', err);
      notify('Não foi possível carregar as modalidades. Tente novamente mais tarde.', 'error');
    });
  }, [loadedSeason?.id]);

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
        season_id: loadedSeason?.id,
        scoring_format_id: chosenScoringFormat ? chosenScoringFormat.id : undefined,
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
              allElementsLoader={() => fetchModalities().then(res => res.map(c => ({ id: c.id, title: c.name })))}
              onSelect={(ele) => {
                if (!ele) return;
                setChosenModalityId(ele.id);
                console.log('Selected modality ID:', ele.id);
                console.log('Modality options:', modalityOptions.find(m => m.id === ele.id));

                let modalityType = modalityOptions.find(m => m.id === ele.id)?.modality_type;
                setChosenScoringFormat(modalityType ? { id: modalityType.id, title: modalityType.name } : null);
                if (!name) setName(ele.title);
              }}
            />
          </div>)}

          {/* Scoring Format */}
          <div className="mb-4">
            <label className="font-medium">
              Formato de Pontuação
            </label>
            <ChoseOneInput
              allElementsLoader={() => modalityTypesApi.getAll({
                season_id: loadedSeason?.id,
              }).then(res => res.map(c => ({ id: c.id, title: c.name })))}
              onSelect={(ele) => {
                if (!ele) return;
                setChosenScoringFormat(ele);
              }}
              elementState={[chosenScoringFormat, (ele) => setChosenScoringFormat(ele)]}
            />
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
