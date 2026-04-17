import { useState } from "react";
import type { MatchDetail } from "../../api/matches";
import MatchPublishResultsModal from "./MatchPublishResultsModal";
import { btn } from "../../styles/buttonStyles";



const MatchResultsComponent = ( {
    match
} : {
    match: MatchDetail;
} ) => {

    const [isPublishing, setIsPublishing] = useState(false);
    const [publishMode, setPublishMode] = useState<'score' | 'position'>('score');

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Resultados do Jogo</h2>

                <div className="flex gap-4 mb-4">
                    <button
                        onClick={() => setIsPublishing(!isPublishing)}
                        className={`flex-1 px-4 py-2 ${btn.primary} rounded-md`}
                    >
                        Publicar Resultados
                    </button>
                </div>
            </div>

            <div className="space-y-4">
                {match.participants.map((participant, index) => (
                    <div key={index} className="flex justify-between items-center">
                        <div>
                            <p className="text-lg font-medium text-gray-700">{participant.name || `Participante ${index + 1}`}</p>
                            {publishMode === 'score' && (
                                <p className="text-sm text-gray-500">Pontuação: {participant.score !== null ? participant.score : 'N/A'}</p>
                            )}
                            {publishMode === 'position' && (
                                <p className="text-sm text-gray-500">Posição: {participant.position !== null ? participant.position : 'N/A'}</p>
                            )}
                        </div>
                    </div>
                ))}
            </div>

        <MatchPublishResultsModal
            controller={[isPublishing, setIsPublishing]}
            match={match}
            onSave={(updatedMatch) => {}}
        />
        </div>
    );
}

export default MatchResultsComponent;
