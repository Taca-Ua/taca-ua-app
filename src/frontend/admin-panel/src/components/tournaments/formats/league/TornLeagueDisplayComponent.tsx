import { useEffect, useState } from "react";
import { type TournamentDetail, tournamentsApi } from "../../../../api/tournaments";
import Button from "../../../utils/Button";
import { useModal } from "../../../../contexts/ModalContext";
import TornLeagueMetaUpdateModal from "./TornLeagueMetaUpdateModal";

export interface LeagueFormatData {
    settings: {
        win_points: number;
        draw_points: number;
        loss_points: number;
        current_round?: number | null;
    },
    standings: {
        competitor_id: string;
        position: number;
        format_meta: {
            played: number;
            points: number;
            wins: number;
            draws: number;
            losses: number;
            points_for: number;
            points_against: number;
            differential: number;
        };
    }[];
}

const TornLeagueDisplayComponent = ({
    tournamentState,
} : {
    tournamentState: [TournamentDetail, React.Dispatch<React.SetStateAction<TournamentDetail | null>>],
}) => {
    const { pushModal } = useModal();

    const [tournament, ] = tournamentState;
    const [formatData, setFormatData] = useState<LeagueFormatData | null>(null);

    const [loadingFormatData, setLoadingFormatData] = useState(false);

    useEffect(() => {
        setLoadingFormatData(true);
        tournamentsApi.getFormatDetails(tournament.id)
          .then(formatDetails => {
            console.log('Fetched format details:', formatDetails);
            // If there are specific details you want to extract and use, you can do it here
            setFormatData(formatDetails as LeagueFormatData);
          })
          .catch(err => {
            console.error('Failed to fetch format details:', err);
          })
          .finally(() => setLoadingFormatData(false));
    }, []);

    const getCompetitorName = (competitorId: string) => {
        const competitor = tournament.competitors.find(c => c.id === competitorId);
        return competitor ? competitor.name : "Competidor Desconecido";
    }

    const renderStandings = () => {
        if (loadingFormatData) {
            return <p>Carregando classificação...</p>;
        }

        if (!formatData) {
            return <p>Detalhes do formato não disponíveis.</p>;
        }

        if (formatData.standings.length === 0) {
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
                        <th className="border-b px-4 py-2">{tournament.modality.point_unit.charAt(0).toUpperCase()}M</th>
                        <th className="border-b px-4 py-2">{tournament.modality.point_unit.charAt(0).toUpperCase()}S</th>
                        <th className="border-b px-4 py-2">Diff</th>
                    </tr>
                </thead>
                <tbody>
                    {formatData.standings.map(entry => (
                        <tr key={entry.competitor_id}>
                            <td className="border-b px-4 py-2">{entry.position}</td>
                            <td className="border-b px-4 py-2">{getCompetitorName(entry.competitor_id)}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.points}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.wins}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.draws}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.losses}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.points_for}</td>
                            <td className="border-b px-4 py-2">{entry.format_meta.points_against}</td>
                            <td className={"border-b px-4 py-2" + (entry.format_meta.differential >= 0 ? " text-green-600" : " text-red-600")}>
                                {entry.format_meta.differential >= 0 ? '+' : ''}{entry.format_meta.differential}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    }

    if (!formatData) {
        return null;
    }

    return (
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex items-center mb-4 justify-between">
            <div className="flex flex-col">
                <h3 className="font-semibold text-blue-900 mb-3">
                Formato: Liga (Pontos: {formatData.settings.win_points} vitória, {formatData.settings.draw_points} empate, {formatData.settings.loss_points} derrota)
                </h3>
                <p className="text-sm text-blue-800 mb-4">
                Ronda atual: {formatData.settings.current_round || 0}
                </p>
            </div>
            <Button
                onClick={() => {pushModal(
                    <TornLeagueMetaUpdateModal
                        formatDataState={[formatData, setFormatData]}
                        tournamentId={tournament.id}
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
