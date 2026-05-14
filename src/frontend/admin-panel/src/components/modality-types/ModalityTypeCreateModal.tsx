import { useState } from "react";
import { modalityTypesApi, type EscalaoRow, type ModalityTypeListItem } from "../../api/modality-types"
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import DefinedStatesMenuComponent from "../utils/costum_menus/DefinedStatesMenuComponent";
import { useNotification } from "../../contexts/NotificationProvider";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";
import { useSeason } from "../../contexts/SeasonContext";

const parsePoints = (raw: string): number[] =>
  raw.split(/[\s,]+/).map(p => parseInt(p.trim())).filter(p => !isNaN(p));

const ModalityTypeCreateModal = ( {
    onCreate
} : {
    onCreate?: (format: ModalityTypeListItem) => void;
} ) => {
    const { notify } = useNotification();
    const { popModal } = useModal();
    const { isAdminGeneral } = useAuth();
    const { loadedSeason } = useSeason();


    const [formatName, setFormatName] = useState('');
    const [formatDescription, setFormatDescription] = useState('');
    const [modalityTypeMode, setModalityTypeMode] = useState<'modality' | 'points' | null>(null);
    const [tournamentCompetitorType, setTournamentCompetitorType] = useState<'individual' | 'team' | null>(null);
    const [escaloes, setEscaloes] = useState<{ escalao: string; minParticipants: number | null; maxParticipants: number | null; points: string }[]>([
        { escalao: 'A', minParticipants: null, maxParticipants: null, points: '' },
    ]);

    const onClose = () => {
        popModal();
        setFormatName('');
        setFormatDescription('');
        setModalityTypeMode(null);
        setTournamentCompetitorType(null);
        setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: '' }]);
    };

    const handleCreateFormat = async () => {
        if (!formatName.trim()) {
            notify('Por favor, preencha o nome do formato.', 'error');
            return;
        }

        if (!modalityTypeMode) {
            notify('Por favor, selecione o modo do formato.', 'error');
            return;
        }

        if (modalityTypeMode === 'modality' && !tournamentCompetitorType) {
            notify('Por favor, selecione o tipo de competidor para o formato de modalidade.', 'error');
            return;
        }

        if (escaloes.length === 0) {
            notify('Por favor, adicione pelo menos um escalão.', 'error');
            return;
        }

        // Validate escaloes
        for (const esc of escaloes) {
            if (!esc.escalao.trim()) {
            notify('Todos os escalões devem ter um nome.', 'error');
            return;
            }
            if (parsePoints(esc.points).length === 0) {
            notify('Todos os escalões devem ter pontuações definidas.', 'error');
            return;
            }
        }

        try {
            const newFormat = await modalityTypesApi.create({
                name: formatName,
                description: formatDescription || undefined,
                escaloes: escaloes.map(esc => ({ ...esc, points: parsePoints(esc.points) })),
                tournament_competitor_type: tournamentCompetitorType!,
                season_id: loadedSeason?.id
            });

            if (onCreate) onCreate(newFormat);
            notify('Formato de prova criado com sucesso!', 'success');
        } catch (err: unknown) {
            console.error('Failed to create scoring format:', err);
            const msg = err instanceof Error ? err.message : '';
            if (msg.toLowerCase().includes('playoff')) {
                notify('Já existe um formato de playoff. Só pode existir um formato de playoff de cada vez.', 'error');
            } else {
                notify('Não foi possível criar o formato de prova. Verifique os dados e tente novamente.', 'error');
            }
        } finally {
            onClose();
        }
    };

    const handleAddEscalao = () => {
        const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
        const nextLetter = letters[escaloes.length] || '';
        setEscaloes([
        ...escaloes,
        { escalao: nextLetter, minParticipants: null, maxParticipants: null, points: '' }
        ]);
    };

    const handleRemoveEscalao = (index: number) => {
        setEscaloes(escaloes.filter((_, i) => i !== index));
    };

    const handleEscalaoChange = (index: number, field: keyof EscalaoRow, value: string | number | null) => {
        const newEscaloes = [...escaloes];
        newEscaloes[index] = { ...newEscaloes[index], [field]: value };
        setEscaloes(newEscaloes);
    };

    if (!isAdminGeneral) return null; // Only general admins can create new modality types

    return (
            <div className="bg-white rounded-lg p-8 w-full max-w-max md:min-w-[500px]">
              <h2 className="text-2xl font-bold mb-6">Criar Formato de Prova</h2>

              <div className="space-y-6">
                <div>
                  <label className="block font-medium mb-2">
                    Nome do Formato <HelpTooltip text="Nome único que identifica este conjunto de regras de pontuação. Ex: 'Modalidades Coletivas Recorrentes'." className="ml-1" /> <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Ex: Modalidades Coletivas Recorrentes"
                    value={formatName}
                    onChange={e => setFormatName(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block font-medium mb-2">Descrição</label>
                  <textarea
                    className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Descrição opcional"
                    rows={2}
                    value={formatDescription}
                    onChange={e => setFormatDescription(e.target.value)}
                  />
                </div>

                {/* Mode */}
                <div>
                  <label className="block font-medium mb-2">
                    Modo de Formato
                    <HelpTooltip
                      text="Define como este formato é aplicado na plataforma."
                      className="ml-1"
                    />
                    <span className="text-red-500">*</span>
                  </label>
                  <DefinedStatesMenuComponent
                    states={[
                      {value: 'modality', label: 'Modalidade', helpText: 'Formato aplicado a uma modalidade, onde os competidores são atletas individuais ou equipas.'},
                      {value: 'points', label: 'Pontuação', helpText: 'Formato que pode ser escolhido por torneios de qualquer modalidade. Apenas afeta pontuações do ranking geral.'},
                    ]}
                    onSelect={(value) => setModalityTypeMode(value as 'modality' | 'points')}
                  />
                </div>

                {(modalityTypeMode === 'modality') && (
                  <div>
                    <label className="block font-medium mb-2">
                      Tipo de Competidor <span className="text-red-500">*</span>
                    </label>
                    <DefinedStatesMenuComponent
                      states={[
                        {value: 'individual', label: 'Individual', helpText: 'Formato destinado a torneios onde os competidores são atletas individuais.'},
                        {value: 'team', label: 'Equipa', helpText: 'Formato destinado a torneios onde os competidores são equipas.'},
                      ]}
                      onSelect={(value) => setTournamentCompetitorType(value as 'individual' | 'team')}
                    />
                  </div>
                )}

                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="block font-medium">
                      Escalões <HelpTooltip text="Categorias de participação dentro do formato (ex: A, B, C). Cada escalão tem os seus próprios limites de participantes e tabela de pontuações." className="ml-1" /> <span className="text-red-500">*</span>
                    </label>
                    <Button
                        onClick={handleAddEscalao}
                        type="info"
                    >
                        + Adicionar Escalão
                    </Button>
                  </div>

                  <div className="space-y-4">
                    {escaloes.map((esc, index) => (
                      <div key={index} className="border border-gray-300 rounded-md p-4 bg-gray-50">
                        <div className="flex justify-between items-start mb-3">
                          <h3 className="font-medium text-lg">Escalão {esc.escalao}</h3>
                          {escaloes.length > 1 && (
                            <button
                              onClick={() => handleRemoveEscalao(index)}
                              className="text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                          <div>
                            <label className="block text-sm font-medium mb-1">Nome do Escalão <HelpTooltip text="Identificador do escalão, tipicamente uma letra (A, B, C) ou nome descritivo." className="ml-1" /></label>
                            <input
                              type="text"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="A, B, C..."
                              value={esc.escalao}
                              onChange={e => handleEscalaoChange(index, 'escalao', e.target.value)}
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1">Mín. Participantes <HelpTooltip text="Número mínimo de equipas/participantes necessários para este escalão se realizar. Deixe vazio se não aplicar." className="ml-1" /></label>
                            <input
                              type="number"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="Ex: 32"
                              value={esc.minParticipants ?? ''}
                              onChange={e => handleEscalaoChange(index, 'minParticipants', e.target.value ? parseInt(e.target.value) : null)}
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1">Máx. Participantes <HelpTooltip text="Número máximo de equipas/participantes permitidos neste escalão. Deixe vazio se não aplicar." className="ml-1" /></label>
                            <input
                              type="number"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="Ex: 40"
                              value={esc.maxParticipants ?? ''}
                              onChange={e => handleEscalaoChange(index, 'maxParticipants', e.target.value ? parseInt(e.target.value) : null)}
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-1">
                            Pontuações (1º, 2º, 3º, ...) <HelpTooltip text="Pontos atribuídos por posição final. O 1º valor é para o 1º lugar, o 2º para o 2º lugar, etc. Separe por espaços ou vírgulas." className="ml-1" position="top" /> <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="text"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 140 130 120 110 90 80 70 60 40 30 20 10"
                            value={esc.points}
                            onChange={e => handleEscalaoChange(index, 'points', e.target.value)}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <Button
                    onClick={onClose}
                    type="secondary"
                    flexible={true}
                >
                    Cancelar
                </Button>
                <Button
                    onClick={handleCreateFormat}
                    type="primary"
                    flexible={true}
                >
                    Criar Formato
                </Button>
              </div>
            </div>
    );
}

export default ModalityTypeCreateModal;
