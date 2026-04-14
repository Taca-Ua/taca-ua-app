import { type TournamentDetail } from "../../api/tournaments"

const TournamentFinishModal = ( {
    controller,
    tournament,
    onSave,
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
    tournament: TournamentDetail,
    onSave: (updatedTournament: TournamentDetail) => void
} ) => {
    const [isOpen, setIsOpen] = controller;
    const numPositions = tournament.scoring_format.points.length;

    if ( !isOpen ) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Finalizar Torneio - Classificação Final
          </h2>

          <p className="text-gray-600 mb-6">
            Selecione os competidores por posição final. Para empates, adicione
            mais competidores na mesma posição.
          </p>

          <div className="space-y-3 mb-6">
            {Array.from({ length: numPositions }, (_, i) => i + 1)
              .filter((position) => activePositions.has(position))
              .map((position) => {
                const competitorsAtPosition = positionAssignments.get(
                  position,
                ) || [""];

                return (
                  <div key={position} className="p-4 bg-gray-50 rounded-md">
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-gray-800 font-semibold">
                        {getPositionLabel(position)}
                      </label>
                      <button
                        type="button"
                        onClick={() => addTieSlot(position)}
                        className="text-sm px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors"
                      >
                        + Empate
                      </button>
                    </div>

                    <div className="space-y-2">
                      {competitorsAtPosition.map(
                        (competitorRecordId, index) => {
                          const selectedElsewhere = new Set(
                            getAssignedCompetitorIds().filter(
                              (id, idx, arr) => {
                                if (id !== competitorRecordId) return true;
                                const first = arr.indexOf(id);
                                return first !== idx;
                              },
                            ),
                          );

                          return (
                            <div
                              key={`${position}-${index}`}
                              className="flex gap-2"
                            >
                              <select
                                value={competitorRecordId}
                                onChange={(e) =>
                                  handleCompetitorChange(
                                    position,
                                    index,
                                    e.target.value,
                                  )
                                }
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                              >
                                <option value="">
                                  Selecione um competidor...
                                </option>
                                {sortedCompetitors.map((competitor) => {
                                  const competitorRecordIdOption =
                                    competitor.id;
                                  const participantName =
                                    getCompetitorName(competitor);
                                  const isDisabled =
                                    selectedElsewhere.has(
                                      competitorRecordIdOption,
                                    ) &&
                                    competitorRecordIdOption !==
                                      competitorRecordId;

                                  return (
                                    <option
                                      key={competitorRecordIdOption}
                                      value={competitorRecordIdOption}
                                      disabled={isDisabled}
                                    >
                                      {participantName} (
                                      {competitor.competitor_type === "team"
                                        ? "Equipa"
                                        : "Atleta"}
                                      ){isDisabled ? " - Já atribuído" : ""}
                                    </option>
                                  );
                                })}
                              </select>

                              {competitorsAtPosition.length > 1 && (
                                <button
                                  type="button"
                                  onClick={() => removeTieSlot(position, index)}
                                  className="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md transition-colors"
                                  title="Remover empate"
                                >
                                  ✕
                                </button>
                              )}
                            </div>
                          );
                        },
                      )}
                    </div>
                  </div>
                );
              })}
          </div>

          {numPositions < tournament.competitors.length && (
            <div className="mb-4 p-3 bg-yellow-100 border border-yellow-400 text-yellow-800 rounded-md text-sm">
              Nota: Apenas os primeiros {numPositions} lugares serão registados.{" "}
              {tournament.competitors.length - numPositions} competidor(es) não
              terão posição atribuída.
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={onClose}
              disabled={finishing}
              className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              disabled={finishing}
              className={`flex-1 px-4 py-2 ${btn.infoStrong} rounded-md disabled:opacity-50`}
            >
              {finishing ? "A finalizar..." : "Finalizar Torneio"}
            </button>
          </div>
        </div>
      </div>
    );
}

export default TournamentFinishModal
