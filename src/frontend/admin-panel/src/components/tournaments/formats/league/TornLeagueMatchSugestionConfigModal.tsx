import { useState } from "react";
import { tournamentsApi, type TournamentMatchSuggestion } from "../../../../api/tournaments";
import Button from "../../../utils/Button";
import { useModal } from "../../../../contexts/ModalContext";
import TornLeagueBulkMatchCreateModal from "./TornLeagueBulkMatchCreateModal";

export interface LeagueSuggestedMatch extends TournamentMatchSuggestion{
    format_specific_data: {
        round_number: number;
    };
}

const TornLeagueMatchSugestionConfigModal = ({
    tournamentId,
}: {
    tournamentId: string,
}) => {
    const { popModal, pushModal } = useModal();

    const [playersPerMatch, setPlayersPerMatch] = useState(2);
    const [numberOfFaceoffs, setNumberOfFaceoffs] = useState(1);

    const handleRequestMatchSuggestions = () => {
        tournamentsApi.getMatchesSuggestions(tournamentId, {
            players_per_match: playersPerMatch,
            number_of_faceoffs: numberOfFaceoffs,
        })
        .then((response) => {
            // Handle the response containing match suggestions
            console.log("Match Suggestions:", response);
            pushModal(<TornLeagueBulkMatchCreateModal
                suggestedMatches={response as LeagueSuggestedMatch[]}
                tournamentId={tournamentId}
            />);
        })
        .catch((error) => {
            // Handle any errors that occur during the request
            console.error("Error fetching match suggestions:", error);
        });
    };

    const handleClose = () => {
        popModal();
    }

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[700px]">
            <h2 className="text-2xl font-bold mb-6">Configurar Sugestões de Jogos</h2>

            <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">
                    Jogadores por Jogo:
                </label>
                <input
                    type="number"
                    value={playersPerMatch}
                    onChange={(e) => setPlayersPerMatch(Number(e.target.value))}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    min={1}
                />
            </div>

            <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">
                    Número de Confrontos:
                </label>
                <input
                    type="number"
                    value={numberOfFaceoffs}
                    onChange={(e) => setNumberOfFaceoffs(Number(e.target.value))}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    min={1}
                />
            </div>

            <div className="flex justify-end mt-6 space-x-4">
                <Button
                    onClick={handleClose}
                    type="secondary"
                    flexible={true}
                >
                    Cancelar
                </Button>
                <Button
                    onClick={handleRequestMatchSuggestions}
                    type="primary"
                    flexible={true}
                >
                    Gerar Sugestões de Jogos
                </Button>
            </div>
        </div>
    );
}

export default TornLeagueMatchSugestionConfigModal
