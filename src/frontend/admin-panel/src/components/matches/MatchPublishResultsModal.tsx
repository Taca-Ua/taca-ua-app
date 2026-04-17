import { useState } from "react";
import { type MatchDetail, matchesApi } from "../../api/matches";
import DefinedStatesMenuComponent from "../utils/costum_menus/DefinedStatesMenuComponent";
import { btn } from "../../styles/buttonStyles";


const ScoreFormComponent = ( {
    participants,
    onSave,
    onClose,
} : {
    participants: string[];
    onSave: (updatedMatch: MatchDetail) => void;
    onClose: () => void;
} ) => {

    const handleSave = () => {
        const updateMatch = async () => {
            try {
                matchesApi.publishResults({
                }).then((updated) => {
                    onSave(updated);
                    onClose();
                }).catch((error) => {
                    console.error("Error publishing results:", error);
                });
            } catch (error) {
                console.error("Error publishing results:", error);
            }
        };
        updateMatch();
    };

    return (
        <div className="space-y-4">
            <div className="mt-4 space-y-2">
                {participants.map((participant, index) => (
                    <div key={index} className="grid grid-cols-2 gap-3 items-center">
                        <label className="text-lg text-gray-700">{participant}</label>
                        <input
                            type="number"
                            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Digite a pontuação"
                        />
                    </div>
                ))}
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
    );
};

const PositionFormComponent = () => {
    return (
        <div className="mt-4 space-y-2">
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

    const [publishMode, setPublishMode] = useState<'score' | 'position'>('score');

    const onClose = () => {
        setIsOpen(false);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-4">Publicar Resultados</h2>
                <DefinedStatesMenuComponent
                    states={[
                        {value: 'score', label: 'Pontuação'},
                        {value: 'position', label: 'Posição'}
                    ]}
                    onSelect={(value) => setPublishMode(value as 'score' | 'position')}
                    initialValue="score"
                />

                {publishMode === 'score' &&
                    <ScoreFormComponent
                        participants={match.participants.map((p) => p.name)}
                        onSave={(updatedMatch) => {
                            onSave(updatedMatch);
                        }}
                        onClose={onClose}
                    />
                }
                {publishMode === 'position' && <PositionFormComponent />}


            </div>
        </div>
    );
}

export default MatchPublishResultsModal;
