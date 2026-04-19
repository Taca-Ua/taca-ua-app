import { useState } from "react";
import { type MatchDetail, matchesApi } from "../../api/matches";
import DefinedStatesMenuComponent from "../utils/costum_menus/DefinedStatesMenuComponent";
import { btn } from "../../styles/buttonStyles";
import { useNotification } from "../../contexts/NotificationProvider";

const ScoreFormComponent = ({
    participants,
    onResultsChange,
}: {
    participants: { id: string; name: string }[];
    onResultsChange: (results: { id: string; score: number }[]) => void;
}) => {
    const [resultsState, setResultsState] = useState<
        { id: string; score: number | null }[]
    >(participants.map((p) => ({ id: p.id, score: null })));

    const handleScoreChange = (participantId: string, score: number) => {
        setResultsState((prev) => {
            const next = prev.map((r) =>
                r.id === participantId ? { ...r, score } : r
            );
            onResultsChange(
                next
                    .filter((r): r is { id: string; score: number } => r.score !== null)
            );
            return next;
        });
    };

    return (
        <div className="space-y-4">
            <div className="mt-4 space-y-2">
                {participants.map((participant, index) => (
                    <div key={index} className="grid grid-cols-2 gap-3 items-center">
                        <label className="text-lg text-gray-700">
                            {participant.name}
                        </label>
                        <input
                            type="number"
                            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Digite a pontuação"
                            value={resultsState.find((r) => r.id === participant.id)?.score ?? ""}
                            onChange={(e) =>
                                handleScoreChange(
                                    participant.id,
                                    Number(e.target.value)
                                )
                            }
                        />
                    </div>
                ))}
            </div>
        </div>
    );
};


const PositionFormComponent = ({
    participants,
    onResultsChange,
} : {
    participants: { id: string; name: string }[];
    onResultsChange: (results: { id: string; position: number }[]) => void;
}) => {
    // Each position holds a participant id or null
    const [resultsState, setResultsState] = useState<(string | null)[]>(Array(participants.length).fill(null));

    // Update results and notify parent
    const handlePositionChange = (participantId: string, position: number) => {
        setResultsState(prev => {
            const next = [...prev];
            next[position - 1] = participantId !== "" ? participantId : null;

            // Notify parent with filled positions
            const results = next
                .map((id, idx) => id ? { id, position: idx + 1 } : null)
                .filter((r): r is { id: string; position: number } => r !== null);
            onResultsChange(results);
            return next;
        });
    };

    // For each position, the available options are those not already selected in other positions
    const getAvailableParticipants = (positionIdx: number) => {
        const selectedIds = resultsState.filter((id, idx) => id !== null && idx !== positionIdx);
        return participants.filter(p => !selectedIds.includes(p.id));
    };

    return (
        <div className="mt-4 space-y-2">
            {Array.from({ length: participants.length }, (_, i) => i + 1).map((position, idx) => (
                <div key={position} className="grid grid-cols-2 gap-3 items-center">
                    <label className="text-lg text-gray-700">
                        Posição {position}
                    </label>
                    <select
                        className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                        value={resultsState[idx] ?? ""}
                        onChange={(e) => handlePositionChange(e.target.value, position)}
                    >
                        <option value="">Selecione um competidor</option>
                        {getAvailableParticipants(idx).map((participant) => (
                            <option key={participant.id} value={participant.id}>
                                {participant.name}
                            </option>
                        ))}
                    </select>
                </div>
            ))}
        </div>
    );
};

const MatchPublishResultsModal = ( {
    controller,
    match,
    onSave
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
    match: MatchDetail,
    onSave: (updatedMatch: MatchDetail) => void
} ) => {

    const [isOpen, setIsOpen] = controller;
    const { notify } = useNotification();

    const [publishMode, setPublishMode] = useState<'score' | 'position'>('score');

    // State to hold the results being edited
    const [scoreResults, setScoreResults] = useState<{id: string, score: number}[]>(match.participants.map((p) => ({id: p.id, score: 0})));
    const [positionResults, setPositionResults] = useState<{id: string, position: number}[]>(match.participants.map((p) => ({id: p.id, position: 0})));

    const onClose = () => {
        setIsOpen(false);
    };

    const handleSave = () => {

        if (publishMode === 'score') {
            // check if all scores are filled
            if (scoreResults.some(r => r.score === null)) {
                notify('Por favor, preencha todas as pontuações antes de publicar.', 'error');
                return;
            }

            matchesApi.publishResults(match.id, {
                participant_results: scoreResults.map(r => ({
                    participant_id: r.id,
                    score: r.score
                })),
                status: 'finished'
            }).then(updatedMatch => {
                notify('Resultados publicados com sucesso!', 'success');
                onSave(updatedMatch);
                onClose();
            }).catch(() => {
                notify('Erro ao publicar resultados. Tente novamente.', 'error');
            });
        }

        if (publishMode === 'position') {
            // check if all positions are filled
            if (positionResults.some(r => r.position === null)) {
                notify('Por favor, preencha todas as posições antes de publicar.', 'error');
                return;
            }

            matchesApi.publishResults(match.id, {
                participant_results: positionResults.map(r => ({
                    participant_id: r.id,
                    position: r.position
                })),
                status: 'finished'
            }).then(updatedMatch => {
                notify('Resultados publicados com sucesso!', 'success');
                onSave(updatedMatch);
                onClose();
            }).catch(() => {
                notify('Erro ao publicar resultados. Tente novamente.', 'error');
            });
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-max">
                <h2 className="text-xl font-bold mb-4">Publicar Resultados</h2>
                <DefinedStatesMenuComponent
                    states={[
                        {value: 'score', label: 'Pontuação'},
                        {value: 'position', label: 'Posição'}
                    ]}
                    onSelect={(value) => setPublishMode(value as 'score' | 'position')}
                    initialValue={publishMode}
                />

                <div className="my-4 gap-4">
                    {publishMode === 'score' &&
                        <ScoreFormComponent
                            participants={match.participants.map((p) => ({id: p.id, name: p.name}))}
                            onResultsChange={(results) => setScoreResults(results)}
                        />
                    }
                    {publishMode === 'position' &&
                        <PositionFormComponent
                            participants={match.participants.map((p) => ({id: p.id, name: p.name}))}
                            onResultsChange={(results) => setPositionResults(results)}
                        />
                    }
                </div>

                <div className="flex gap-4">
                    <button
                        onClick={onClose}
                        className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md`}
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSave}
                        className={`flex-1 px-4 py-2 ${btn.primary} rounded-md`}
                    >
                        Publicar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default MatchPublishResultsModal;
