import { useState } from "react";
import { useModal } from "../../contexts/ModalContext";
import { matchesApi, type MatchDetail, type MatchLineup } from "../../api/matches";
import ChooseMultipleModal from "../utils/costum_menus/ChoseMultipleModal";
import { athletesApi } from "../../api/athletes";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";

type PlayerDraft = {
    player_id: string;
    jersey_number: string;
    is_starter: boolean;
};

const MatchTeamLineupModal = ({
    matchState,
    lineup,
}: {
    matchState: [MatchDetail, React.Dispatch<React.SetStateAction<MatchDetail | null>>];
    lineup: MatchLineup;
}) => {
    const { popModal, pushModal } = useModal();
    const { notify } = useNotification();

    const [match, setMatch] = matchState;

    const [isEditMode, setIsEditMode] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [drafts, setDrafts] = useState<PlayerDraft[]>([]);

    const onClose = () => popModal();

    const handleDownloadTeamSheet = async (participantId: string) => {
        try {
            const blob = await matchesApi.getMatchTeamSheet(match.id, participantId);
            const url = window.URL.createObjectURL(blob);
            window.open(url, "_blank");
            setTimeout(() => window.URL.revokeObjectURL(url), 10000);
        } catch (err) {
            console.error("Error downloading team sheet:", err);
            notify(
                err instanceof Error
                    ? err.message
                    : "Não foi possível descarregar a ficha de equipa. Tente novamente.",
                "error",
            );
        }
    };

    const enterEditMode = () => {
        setDrafts(
            lineup.lineup.map((p) => ({
                player_id: p.player_id,
                jersey_number: p.jersey_number?.toString() ?? "",
                is_starter: p.is_starter,
            })),
        );
        setIsEditMode(true);
    };

    const cancelEditMode = () => {
        setIsEditMode(false);
        setDrafts([]);
    };

    const updateDraft = (
        player_id: string,
        field: keyof Omit<PlayerDraft, "player_id">,
        value: string | boolean,
    ) => {
        setDrafts((prev) =>
            prev.map((d) =>
                d.player_id === player_id ? { ...d, [field]: value } : d,
            ),
        );
    };

    const saveAll = async () => {
        setIsSaving(true);

        await matchesApi.updateLineup(match.id, {
            participant: lineup.participant_id,
            players: drafts.map((d) => ({
                player_id: d.player_id,
                is_starter: d.is_starter,
                jersey_number: d.jersey_number ? parseInt(d.jersey_number) : null,
            })),
        }).then((updatedMatch) => {
            notify("Convocatória actualizada com sucesso", "success")
            setMatch(updatedMatch);
            lineup.lineup = updatedMatch.lineups.find(l => l.participant_id === lineup.participant_id)?.lineup || [];
            setIsEditMode(false);
            setDrafts([]);
        }).catch((err) => {
            console.error("Error saving lineup details:", err);
            notify("Não foi possível guardar as alterações. Tente novamente.", "error");
        }).finally(() => {
            setIsSaving(false);
        });
    };

    return (
      <div className="bg-white rounded-xl p-8 w-full max-w-md md:min-w-[700px] shadow-lg">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Convocatórias de{" "}
            {match.participants.find((p) => p.id === lineup.participant_id)
              ?.name || lineup.participant_id}
          </h2>

          {!isEditMode ? (
            <button
              onClick={enterEditMode}
              className="shrink-0 flex items-center gap-2 rounded-lg border border-gray-300 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600 text-gray-500 text-sm font-medium px-3 py-2 transition-colors"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 112.828 2.828L11.828 15.828a2 2 0 01-1.414.586H8v-2.414a2 2 0 01.586-1.414z"
                />
              </svg>
              Editar detalhes
            </button>
          ) : (
            <span
              className="shrink-0 inline-flex items-center gap-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-600 text-sm font-semibold px-3 py-2"
            >
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              Modo de edição
            </span>
          )}
        </div>

        {/* Top action buttons — hidden in edit mode */}
        {!isEditMode && (
          <div className="flex space-x-3 mb-6">
            <Button
              onClick={() => {
                pushModal(
                  <ChooseMultipleModal
                    allElementsLoader={() =>
                      athletesApi.getAll({
                        team_id: match.participants.find((p) => p.id === lineup.participant_id)?.entity_id,
                      }).then((res) =>
                        res.map((athlete) => ({
                          id: athlete.id,
                          title: athlete.full_name,
                          subTitle: `Curso: ${athlete.course.abbreviation}`,
                        })),
                      )
                    }
                    initialChosenElementsIds={lineup.lineup.map(
                      (player) => player.player_id,
                    )}
                    onSave={(selectedIds) => {
                      matchesApi
                        .assignLineup(match.id, {
                          participant: lineup.participant_id,
                          players: selectedIds.map((player_id) => player_id.id),
                        })
                        .then((updatedMatch) =>{
                          setMatch(updatedMatch);
                          lineup.lineup = updatedMatch.lineups.find(l => l.participant_id === lineup.participant_id)?.lineup || [];
                          notify(
                            "Convocatória actualizada com sucesso",
                            "success",
                          )
                        })
                        .catch((error) => {
                          notify(
                            "Não foi possível actualizar a convocatória. Tente novamente.",
                            "error",
                          );
                          console.error("Error updating lineup:", error);
                        });
                    }}
                    showSummary={true}
                  />,
                );
              }}
              type="primary"
              flexible={true}
            >
              +/- Escolher jogadores
            </Button>

            <Button
              onClick={() => handleDownloadTeamSheet(lineup.participant_id)}
              type="info"
              padding="w-full px-4 py-3 flex items-center justify-center"
              flexible={true}
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Baixar Ficha de Jogo
            </Button>
          </div>
        )}

        {/* Column headers in edit mode */}
        {isEditMode && (
          <div className="flex items-center gap-4 px-1 mb-1">
            <span className="flex-1 text-xs font-semibold uppercase tracking-wider text-gray-400">
              Jogador
            </span>
            <span className="w-24 text-xs font-semibold uppercase tracking-wider text-gray-400 text-center">
              Nº Camisola
            </span>
            <span className="w-44 text-xs font-semibold uppercase tracking-wider text-gray-400 text-center">
              Papel
            </span>
          </div>
        )}

        {/* Player list */}
        <ul className="divide-y divide-gray-100">
          {lineup.lineup.map((player) => {
            const draft = drafts.find((d) => d.player_id === player.player_id);

            return (
              <li key={player.player_id} className="py-3.5">
                {isEditMode && draft ? (
                  /* ── Edit row ── */
                  <div className="flex items-center gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 truncate">
                        {player.player_name}
                      </p>
                      <p className="text-xs text-gray-400">
                        {player.player_course}
                      </p>
                    </div>

                    <div className="w-24 flex justify-center">
                      <input
                        type="number"
                        min={1}
                        max={99}
                        value={draft.jersey_number}
                        onChange={(e) =>
                          updateDraft(
                            player.player_id,
                            "jersey_number",
                            e.target.value,
                          )
                        }
                        placeholder="—"
                        className="w-16 rounded-lg border border-gray-300 px-2 py-1.5 text-sm text-center
                                                                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                                                                 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none
                                                                 [&::-webkit-inner-spin-button]:appearance-none"
                      />
                    </div>

                    <div className="w-44 flex justify-center">
                      <div className="flex rounded-lg overflow-hidden border border-gray-200 text-sm font-medium w-full">
                        <button
                          onClick={() =>
                            updateDraft(player.player_id, "is_starter", true)
                          }
                          className={`flex-1 py-1.5 transition-colors ${
                            draft.is_starter
                              ? "bg-green-500 text-white"
                              : "bg-white text-gray-400 hover:bg-gray-50"
                          }`}
                        >
                          Titular
                        </button>
                        <button
                          onClick={() =>
                            updateDraft(player.player_id, "is_starter", false)
                          }
                          className={`flex-1 py-1.5 border-l border-gray-200 transition-colors ${
                            !draft.is_starter
                              ? "bg-gray-600 text-white"
                              : "bg-white text-gray-400 hover:bg-gray-50"
                          }`}
                        >
                          Suplente
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* ── Display row ── */
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-base font-semibold text-gray-900 truncate">
                        {player.player_name}
                      </p>
                      <p className="text-sm text-gray-400">
                        Curso: {player.player_course}
                      </p>
                    </div>

                    <div className="flex items-center gap-4 shrink-0">
                      {player.jersey_number != null ? (
                        <span
                          className="inline-flex items-center justify-center w-8 h-8 rounded-full
                                                                             bg-gray-100 text-sm font-bold text-gray-700"
                        >
                          {player.jersey_number}
                        </span>
                      ) : (
                        <span
                          className="inline-flex items-center justify-center w-8 h-8 rounded-full
                                                                             bg-gray-50 text-sm text-gray-300"
                        >
                          —
                        </span>
                      )}

                      {player.is_starter ? (
                        <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-green-600">
                          <span className="w-2 h-2 rounded-full bg-green-500" />
                          Titular
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-400">
                          <span className="w-2 h-2 rounded-full bg-gray-300" />
                          Suplente
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>

        {/* Footer */}
        <div className="mt-6 flex justify-end gap-3">
          {isEditMode ? (
            <>
              <Button
                onClick={cancelEditMode}
                disabled={isSaving}
                type="secondary"
                flexible={true}
              >
                Cancelar
              </Button>
              <Button
                onClick={saveAll}
                disabled={isSaving}
                type="primary"
                flexible={true}
              >
                Guardar alterações
              </Button>
            </>
          ) : (
            <Button onClick={onClose} type="secondary" flexible={true}>
              Fechar
            </Button>
          )}
        </div>
      </div>
    );
};

export default MatchTeamLineupModal;
