import { useState } from "react";
import { type EscalaoRow, type ModalityTypeDetail, modalityTypesApi } from "../../api/modality-types";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";

const parsePoints = (raw: string): number[] =>
  raw.split(/[\s,]+/).map(p => parseInt(p.trim())).filter(p => !isNaN(p));

const ModalityTypeEditModal = ( {
    modalityTypeState
} : {
    modalityTypeState: [ModalityTypeDetail, React.Dispatch<React.SetStateAction<ModalityTypeDetail | null>>];
} ) => {

    const { notify } = useNotification();
    const { popModal } = useModal();
    const { isAdminGeneral } = useAuth();


    const [modalityType, setModalityType] = modalityTypeState;
    const [formatName, setFormatName] = useState(modalityType.name);
    const [formatDescription, setFormatDescription] = useState(modalityType.description || "");
    const [isPlayoff, setIsPlayoff] = useState(modalityType.is_playoff);
    const [tournamentCompetitorType, setTournamentCompetitorType] = useState(modalityType.tournament_competitor_type);
    const [escaloes, setEscaloes] = useState<{ escalao: string; minParticipants: number | null; maxParticipants: number | null; points: string }[]>(
        modalityType.escaloes.map(e => ({
            escalao: e.escalao,
            minParticipants: e.minParticipants,
            maxParticipants: e.maxParticipants,
            points: e.points.join(" "),
        }))
    );

    const onClose = () => {
        popModal();
        setFormatName(modalityType.name);
        setFormatDescription(modalityType.description || "");
        setIsPlayoff(modalityType.is_playoff);
        setTournamentCompetitorType(modalityType.tournament_competitor_type);
        setEscaloes(modalityType.escaloes.map(e => ({
            escalao: e.escalao,
            minParticipants: e.minParticipants,
            maxParticipants: e.maxParticipants,
            points: e.points.join(" "),
        })));
    };

    const handleUpdateFormat = async () => {
        if (!formatName.trim()) {
          notify('Por favor, preencha o nome do formato.', 'error');
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

        // If user is deselecting playoff, require tournament_competitor_type
        if (modalityType.is_playoff && !isPlayoff && !tournamentCompetitorType) {
          notify('Selecione o tipo de competidor (Individual ou Equipa) ao remover o formato playoff.', 'error');
          return;
        }

        try {

            // TODO: API call to update scoring format
            const updatedFormat = await modalityTypesApi.update(modalityType.id, {
                name: formatName,
                description: formatDescription || undefined,
                is_playoff: isPlayoff,
                escaloes: escaloes.map(esc => ({ ...esc, points: parsePoints(esc.points) })),
                tournament_competitor_type: tournamentCompetitorType,
            });

            setModalityType(updatedFormat);
            notify('Formato de prova atualizado com sucesso!', 'success');
        } catch (err: unknown) {
            console.error('Failed to update scoring format:', err);
            const msg = err instanceof Error ? err.message : '';
            if (msg.toLowerCase().includes('playoff')) {
                notify('Já existe um formato de playoff. Só pode existir um formato de playoff de cada vez.', 'error');
            } else {
                notify('Não foi possível guardar as alterações ao formato de prova. Tente novamente.', 'error');
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

    if (!isAdminGeneral) return null;  // extra layer of protection in case this component is used somewhere else by mistake without the proper checks

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-max md:min-w-[500px]">
          <h2 className="text-2xl font-bold mb-6">Editar Formato de Prova</h2>

          <div className="space-y-6">
            <div>
              <label className="block font-medium mb-2">
                Nome do Formato{" "}
                <HelpTooltip
                  text="Nome único que identifica este conjunto de regras de pontuação. Ex: 'Modalidades Coletivas Recorrentes'."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Ex: Modalidades Coletivas Recorrentes"
                value={formatName}
                onChange={(e) => setFormatName(e.target.value)}
              />
            </div>

            <div>
              <label className="block font-medium mb-2">Descrição</label>
              <textarea
                className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Descrição opcional"
                rows={2}
                value={formatDescription}
                onChange={(e) => setFormatDescription(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="edit-is-playoff"
                checked={isPlayoff}
                onChange={(e) => setIsPlayoff(e.target.checked)}
                className="w-4 h-4 accent-amber-500 cursor-pointer"
              />
              <label
                htmlFor="edit-is-playoff"
                className="font-medium cursor-pointer select-none"
              >
                Formato Playoff
              </label>
              <span className="text-sm text-gray-500">
                (só pode existir um formato de playoff de cada vez)
              </span>
            </div>

            {!isPlayoff && (
              <div>
                <label className="block font-medium mb-2">
                  Tipo de Competidor <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className={`flex-1 py-2 rounded-md border transition-colors font-semibold ${tournamentCompetitorType === "team" ? "bg-teal-500 text-white border-teal-600" : "bg-white text-teal-700 border-gray-300"}`}
                    onClick={() => setTournamentCompetitorType("team")}
                  >
                    Equipa
                  </button>
                  <button
                    type="button"
                    className={`flex-1 py-2 rounded-md border transition-colors font-semibold ${tournamentCompetitorType === "individual" ? "bg-teal-500 text-white border-teal-600" : "bg-white text-teal-700 border-gray-300"}`}
                    onClick={() => setTournamentCompetitorType("individual")}
                  >
                    Individual
                  </button>
                </div>
              </div>
            )}

            <div>
              <div className="flex justify-between items-center mb-3">
                <label className="block font-medium">
                  Escalões{" "}
                  <HelpTooltip
                    text="Categorias de participação dentro do formato (ex: A, B, C). Cada escalão tem os seus próprios limites de participantes e tabela de pontuações."
                    className="ml-1"
                  />{" "}
                  <span className="text-red-500">*</span>
                </label>
              </div>

              <div className="space-y-4">
                {escaloes.map((esc, index) => (
                  <div
                    key={index}
                    className="border border-gray-300 rounded-md p-4 bg-gray-50"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-medium text-lg">
                        Escalão {esc.escalao}
                      </h3>
                      {escaloes.length > 1 && (
                        <button
                          onClick={() => handleRemoveEscalao(index)}
                          className="text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                        >
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Nome do Escalão{" "}
                          <HelpTooltip
                            text="Identificador do escalão, tipicamente uma letra (A, B, C) ou nome descritivo."
                            className="ml-1"
                          />
                        </label>
                        <input
                          type="text"
                          className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                          placeholder="A, B, C..."
                          value={esc.escalao}
                          onChange={(e) =>
                            handleEscalaoChange(
                              index,
                              "escalao",
                              e.target.value,
                            )
                          }
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Mín. Participantes{" "}
                          <HelpTooltip
                            text="Número mínimo de equipas/participantes necessários para este escalão se realizar. Deixe vazio se não aplicar."
                            className="ml-1"
                          />
                        </label>
                        <input
                          type="number"
                          className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                          placeholder="Ex: 32"
                          value={esc.minParticipants ?? ""}
                          onChange={(e) =>
                            handleEscalaoChange(
                              index,
                              "minParticipants",
                              e.target.value ? parseInt(e.target.value) : null,
                            )
                          }
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Máx. Participantes{" "}
                          <HelpTooltip
                            text="Número máximo de equipas/participantes permitidos neste escalão. Deixe vazio se não aplicar."
                            className="ml-1"
                          />
                        </label>
                        <input
                          type="number"
                          className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                          placeholder="Ex: 40"
                          value={esc.maxParticipants ?? ""}
                          onChange={(e) =>
                            handleEscalaoChange(
                              index,
                              "maxParticipants",
                              e.target.value ? parseInt(e.target.value) : null,
                            )
                          }
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Pontuações (1º, 2º, 3º, ...){" "}
                        <HelpTooltip
                          text="Pontos atribuídos por posição final. O 1º valor é para o 1º lugar, o 2º para o 2º lugar, etc. Separe por espaços ou vírgulas."
                          className="ml-1"
                          position="top"
                        />{" "}
                        <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                        placeholder="Ex: 140 130 120 110 90 80 70 60 40 30 20 10"
                        value={esc.points}
                        onChange={(e) =>
                          handleEscalaoChange(index, "points", e.target.value)
                        }
                      />
                    </div>
                  </div>
                ))}
                <Button
                    onClick={handleAddEscalao}
                    type="info"
                >
                    + Adicionar Escalão
                </Button>
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
                onClick={handleUpdateFormat}
                type="primary"
                flexible={true}
            >
                Guardar Alterações
            </Button>
          </div>
        </div>
    );
}

export default ModalityTypeEditModal;
