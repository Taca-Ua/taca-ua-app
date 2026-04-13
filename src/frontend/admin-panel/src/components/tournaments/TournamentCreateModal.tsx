import { useState, useEffect } from 'react';
import HelpTooltip from '../HelpTooltip';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type Tournament, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { seasonsApi, type Season } from '../../api/seasons';
import { btn } from '../../styles/buttonStyles';

interface TournamentCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (tournament: Tournament) => void;
  fixedModalityId?: string; // If provided, modality is fixed and not selectable
  fixedModalityName?: string; // Display name for fixed modality
}

const TournamentCreateModal = ({
  isOpen,
  onClose,
  onCreate,
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
  const { notify } = useNotification();

  const isFixedModality = !!fixedModalityId;

  // Fetch modalities if needed (only when modality is not fixed)
  useEffect(() => {
    if (isFixedModality) return;

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
  }, [isFixedModality]);

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
    setLoading(true);
    try {
      const newTournament: TournamentCreate = {
        name,
        modality_id: modalityId,
        is_playoff: isPlayoff,
        competitors: [],
        ...(seasonId ? { season_id: seasonId } : {}),
      };
      const createdTournament = await tournamentsApi.create(newTournament);
      onCreate(createdTournament);
      handleClose();
    } catch (err) {
      console.error('Failed to create tournament:', err);
      notify('Não foi possível criar o torneio. Verifique os dados e tente novamente.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
    // Reset form
    setName(fixedModalityName || '');
    setNameManuallyEdited(!!fixedModalityName);
    setModalityId(fixedModalityId || '');
    setIsPlayoff(false);
    setSeasonId('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-8 rounded-lg w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4">Criar Torneio</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
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
              onChange={(e) => {
                setName(e.target.value);
                setNameManuallyEdited(true);
              }}
              className="w-full border border-gray-300 rounded-md p-2"
              required
            />
          </div>

          <div>
            <label className="font-medium">
              Modalidade{' '}
              {!isFixedModality && (
                <HelpTooltip
                  text="Desporto ou atividade para o qual este torneio é organizado. A modalidade determina as regras de inscrição (equipas vs atletas)."
                  className="ml-1"
                />
              )}{' '}
              {!isFixedModality && <span className="text-red-500">*</span>}
            </label>
            {isFixedModality ? (
              <div className="w-full border border-gray-300 rounded-md p-2 bg-gray-100 text-gray-700">
                {fixedModalityName}
              </div>
            ) : (
              <select
                value={modalityId}
                onChange={(e) => setModalityId(e.target.value)}
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
            )}
          </div>

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
            <button
              type="button"
              onClick={handleClose}
              className={`px-4 py-2 ${btn.secondary} rounded-md`}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className={`px-4 py-2 ${btn.primary} rounded-md`}
              disabled={loading}
            >
              {loading ? 'A criar...' : 'Criar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TournamentCreateModal;
