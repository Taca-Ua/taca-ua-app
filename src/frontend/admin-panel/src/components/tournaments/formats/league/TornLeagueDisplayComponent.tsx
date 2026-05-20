import { useEffect, useState } from "react";
import { type TournamentDetail, type TournamentStandingsEntry, tournamentsApi } from "../../../../api/tournaments";
import Button from "../../../utils/Button";
import { useModal } from "../../../../contexts/ModalContext";
import TornLeagueMetaUpdateModal from "./TornLeagueMetaUpdateModal";

interface LeagueFormatData {
    points_win: number;
    points_draw: number;
    points_loss: number;
    current_round: number;
}

const TornLeagueDisplayComponent = ({
    tournamentState,
} : {
    tournamentState: [TournamentDetail, React.Dispatch<React.SetStateAction<TournamentDetail | null>>],
}) => {
    const { pushModal } = useModal();

    console.log("Rendering TornLeagueDisplayComponent with tournamentState:", tournamentState);
    const [tournament, ] = tournamentState;

    const data = tournament.format_data as LeagueFormatData;

    const [currentStandings, setCurrentStandings] = useState<TournamentStandingsEntry[]>([]);
    const [loadingStandings, setLoadingStandings] = useState(false);

    const loadStandings = () => {
        setLoadingStandings(true);
        tournamentsApi.getStandings(tournament.id)
          .then(setCurrentStandings)
          .catch(err => {
            console.error('Failed to fetch standings:', err);

            if (err.response && err.response.status === 404) {
              // Standings not found, likely because the tournament hasn't started yet
              setCurrentStandings([]);
            }
          })
          .finally(() => setLoadingStandings(false));
    };

    useEffect(() => {
        loadStandings();
    }, [data.current_round]);

    const renderStandings = () => {
        if (loadingStandings) {
            return <p>Carregando classificação...</p>;
        }

        if (currentStandings.length === 0) {
            return <p>Classificação ainda não disponível.</p>;
        }

        return (
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr>
                        <th className="border-b px-4 py-2">Posição</th>
                        <th className="border-b px-4 py-2">Competidor</th>
                        <th className="border-b px-4 py-2">Pontos</th>
                        <th className="border-b px-4 py-2">Vitórias</th>
                        <th className="border-b px-4 py-2">Empates</th>
                        <th className="border-b px-4 py-2">Derrotas</th>
                    </tr>
                </thead>
                <tbody>
                    {currentStandings.map(entry => (
                        <tr key={entry.competitor_id}>
                            <td className="border-b px-4 py-2">{entry.position}</td>
                            <td className="border-b px-4 py-2">{entry.competitor_name}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.points}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.wins}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.draws}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.losses}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    }

    return (
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex items-center mb-4 justify-between">
            <div className="flex flex-col">
                <h3 className="font-semibold text-blue-900 mb-3">
                Formato: Liga (Pontos: {data.points_win} vitória, {data.points_draw} empate, {data.points_loss} derrota)
                </h3>
                <p className="text-sm text-blue-800 mb-4">
                Ronda atual: {data.current_round || 0}
                </p>
            </div>
            <Button
                onClick={() => {pushModal(
                    <TornLeagueMetaUpdateModal
                        tournamentState={tournamentState}
                        onSave={() => loadStandings()}
                    />
                )}}
                type="primary"
            >
                Atualizar Classificação
            </Button>
        </div>

        {renderStandings()}
      </div>
    );
};

export default TornLeagueDisplayComponent;
