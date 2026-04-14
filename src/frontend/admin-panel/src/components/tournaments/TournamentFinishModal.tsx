import { tournamentsApi, type TournamentDetail } from "../../api/tournaments";
import { useNotification } from "../../contexts/NotificationProvider";
import { useState, useMemo, useEffect } from "react";
import { DragDropContext, Droppable, Draggable, type DropResult } from "@hello-pangea/dnd";
import { btn } from "../../styles/buttonStyles";

interface TournamentCompetitor {
  id: string;
  name: string;
  course_name: string;
}

// Left column: Positions
function PositionsColumn({
  standings,
  competitorsById,
  getPositionLabel,
}: {
  numPositions: number;
  standings: { [id: string]: number };
  competitorsById: Record<string, TournamentCompetitor>;
  getPositionLabel: (position: number) => string;
}) {

  const maxPosition = Object.values(standings).reduce((max, pos) => Math.max(max, pos), 0) + 1;

  const renderCompetitor = (id: string, index: number) => {
    const competitor = competitorsById[id];
    if (!competitor) return null;
    return (
      <Draggable draggableId={id} index={index} key={id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            className={`px-4 py-2 rounded bg-blue-100 text-blue-900 shadow flex items-center gap-2 ${snapshot.isDragging ? "ring-2 ring-blue-400" : ""}`}
          >
            <span className="font-medium">{competitor.name}</span>
            <span className="text-xs text-gray-500">({competitor.course_name})</span>
          </div>
        )}
      </Draggable>
    );
  };

  const renderPosition = (position: number) => {
    const assigned = Object.entries(standings).filter(([_, pos]) => pos === position).map(([id]) => id);
    return (
      <Droppable droppableId={position.toString()} key={position} direction="vertical">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`bg-gray-50 rounded-md p-4 min-h-[64px] border-2 ${snapshot.isDraggingOver ? "border-blue-400" : "border-gray-200"}`}
          >
            <div className="font-semibold mb-2 text-gray-800 flex items-center gap-2">
              {getPositionLabel(position)}
            </div>
            <div className="flex flex-col gap-2 min-h-[32px]">
              {assigned.map((id, idx) => renderCompetitor(id, idx))}
              {provided.placeholder}
            </div>
          </div>
        )}
      </Droppable>
    );
  };

  return (
    <div className="flex-1 grid-cols-1 space-y-4 overflow-y-auto max-h-[60vh] min-h-0 pr-1">
      {Array.from({ length: maxPosition }, (_, i) => i + 1).map((position) => renderPosition(position))}
    </div>
  );
}

// Right column: Unassigned competitors
function UnassignedColumn({
  unassigned,
  competitorsById,
}: {
  unassigned: string[];
  competitorsById: Record<string, { id: string; name: string; course_name: string }>;
}) {
  return (
    <div className="w-72 grid flex flex-col min-h-0">
      {/* <h3 className="font-semibold mb-2 text-gray-800">Competidores por atribuir</h3> */}
      <Droppable droppableId="unassigned" direction="vertical">
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`bg-gray-50 rounded-md p-4 min-h-[64px] border-2 space-y-2 ${snapshot.isDraggingOver ? "border-blue-400" : "border-gray-200"} overflow-y-auto max-h-[60vh]`}
          >
            {unassigned.map((id, idx) => {
              const competitor = competitorsById[id];
              if (!competitor) return null;
              return (
                <Draggable draggableId={id} index={idx} key={id}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className={`px-4 py-2 rounded bg-white text-gray-800 shadow flex items-center gap-2 ${snapshot.isDragging ? "ring-2 ring-blue-400" : ""}`}
                    >
                      <span className="font-medium">{competitor.name}</span>
                      <span className="text-xs text-gray-500">({competitor.course_name})</span>
                    </div>
                  )}
                </Draggable>
              );
            })}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  );
}

const TournamentFinishModal = ({
  controller,
  tournament,
  onSave,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  tournament: TournamentDetail;
  onSave: (updatedTournament: TournamentDetail) => void;
}) => {
  const { notify } = useNotification();
  const [isOpen, setIsOpen] = controller;
  const numPositions = tournament.scoring_format.points.length;

  // State: position assignments and unassigned competitors
  const [standings, setStandings] = useState<{ [id: string]: number }>({});
  const [unassigned, setUnassigned] = useState<string[]>(() => tournament.competitors.map((c) => c.id));

  const competitorsById = useMemo(() => {
    const map: Record<string, (typeof tournament.competitors)[0]> = {};
    for (const c of tournament.competitors) map[c.id] = c;
    return map;
  }, [tournament.competitors]);

  const getPositionLabel = (position: number) => {
    let cur_pos = 1;
    for (let i = 1; i < position; i++) {
      let count = Object.values(standings).filter((pos) => pos === i).length;
      if (count === 0) count++;
      if (count > 0) cur_pos += count;
    }

    if (cur_pos === 1) return "🥇 1º Lugar";
    if (cur_pos === 2) return "🥈 2º Lugar";
    if (cur_pos === 3) return "🥉 3º Lugar";
    return `${cur_pos}º Lugar`;
  };

  const onDragEnd = (result: DropResult) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    if (destination.droppableId === "unassigned") {
      // Moving back to unassigned
      setStandings((prev) => {
        const newStandings = { ...prev };
        delete newStandings[draggableId];
        return newStandings;
      });
      setUnassigned((prev) => {
        const newUnassigned = [...prev];
        newUnassigned.splice(destination.index, 0, draggableId);
        return newUnassigned;
      });
    } else {
      // Assigning to a position
      const newPosition = parseInt(destination.droppableId);
      setStandings((prev) => ({
        ...prev,
        [draggableId]: newPosition,
      }));
      setUnassigned((prev) => prev.filter((id) => id !== draggableId));
    }
  };

  const handleSave = () => {

    console.log("Final standings:", standings);

    // prepare standings
    const finalStandings: { [id: string]: number } = {};
    let cur_pos = 1;
    const maxPosition = Object.values(standings).reduce((max, pos) => Math.max(max, pos), 0) + 1;
    for(let i = 1; i < maxPosition; i++) {
      let count = 0;
      for(const [id, pos] of Object.entries(standings)) {
        if(pos === i) {
          finalStandings[id] = cur_pos;
          count++;
        }
      }
      if (count === 0) {
        notify(`Atenção: Não há competidores atribuídos à posição ${cur_pos}.`, "error");
        return;
      };
      cur_pos += count;
    }

    const finishTournament = async () => {
      try {
        const result = await tournamentsApi.finish(tournament.id, {
          ranking_entries: Object.entries(finalStandings).map(([id, position]) => ({
            competitor_id: id,
            position: position,
          })),
        });
        onSave(result);
        notify("Torneio finalizado com sucesso!", "info");
        setIsOpen(false);
      } catch (error) {
        console.error("Error finalizing tournament:", error);
        notify("Erro ao finalizar torneio.", "error");
      }
    };

    finishTournament();
  };

  const onClose = () => {
    setStandings({});
    setUnassigned(tournament.competitors.map((c) => c.id));
    setIsOpen(false);
  }

  useEffect(() => {
    if (!isOpen) return;

    // reset state when opening
    setStandings({});
    setUnassigned(tournament.competitors.map((c) => c.id));
  }, [isOpen, tournament.competitors]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 w-[900px] h-[80vh] max-w-full mx-4 flex flex-col">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Finalizar Torneio - Classificação Final
        </h2>

        <p className="text-gray-600 mb-6">
          Arraste os competidores para as posições finais. Para empates, arraste mais de um competidor para a mesma posição.
        </p>

        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex gap-8 mb-8 flex-1 min-h-0">
            <PositionsColumn
              numPositions={numPositions}
              standings={standings}
              competitorsById={competitorsById}
              getPositionLabel={getPositionLabel}
            />
            <UnassignedColumn
              unassigned={unassigned}
              competitorsById={competitorsById}
            />
          </div>
        </DragDropContext>

        {numPositions < tournament.competitors.length && (
          <div className="mb-4 p-3 bg-yellow-100 border border-yellow-400 text-yellow-800 rounded-md text-sm">
            Nota: Apenas os primeiros {numPositions} lugares serão registados. {tournament.competitors.length - numPositions} competidor(es) não terão posição atribuída.
          </div>
        )}

        <div className="flex gap-4">
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className={`flex-1 px-4 py-2 ${btn.infoStrong} rounded-md disabled:opacity-50`}
          >
            Finalizar Torneio
          </button>
        </div>
      </div>
    </div>
  );
};


export default TournamentFinishModal;
