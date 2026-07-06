import { useMemo, useState } from "react";
import { tournamentsApi, type TournamentDetail } from "../../../../api/tournaments";
import { type ApiError } from "../../../../api/client";
import Button from "../../../utils/Button";
import { useModal } from "../../../../contexts/ModalContext";
import {type LeagueSuggestedMatch} from "./TornLeagueMatchSugestionConfigModal";
import { useNotification } from "../../../../contexts/NotificationProvider";

type Competitor = TournamentDetail["competitors"][0];

const MatchRow = ({
    match,
    competitorsMap,
} : {
    match: LeagueSuggestedMatch,
    competitorsMap: Record<string, Competitor>,
}) => {
    const renderCompetitorName = (id: string) => {
        return competitorsMap[id]?.name || id;
    }

    return (
        <div className="grid grid-cols-3 gap-4 items-center">
            <div className="col-span-1">
                <span className="font-semibold">{renderCompetitorName(match.competitors_ids[0])}</span>
            </div>
            <div className="col-span-1 text-center">
                <span className="font-semibold">vs</span>
            </div>
            <div className="col-span-1">
                <span className="font-semibold">{renderCompetitorName(match.competitors_ids[1])}</span>
            </div>
        </div>
    );
}


const RoundDisplay = ({
    roundNumber,
    matches,
    competitorsMap,
} : {
    roundNumber: number;
    matches: LeagueSuggestedMatch[];
    competitorsMap: Record<string, Competitor>;
}) => {
    const [collapsed, setCollapsed] = useState(false);

    const filteredMatches = matches.filter(match => match.format_specific_data.round_number === roundNumber);

    return (
        <div className="border rounded p-4 mb-4">
            <div className="flex items-center justify-between cursor-pointer" onClick={() => setCollapsed(!collapsed)}>
                <h3 className="text-xl font-semibold mb-4">Rodada {roundNumber}</h3>
                <button className="text-sm text-blue-500">
                    {collapsed ? "Mostrar" : "Ocultar"}
                </button>
            </div>

            {!collapsed && (
            <div className="space-y-4">
                {filteredMatches.map((match, index) => (
                    <MatchRow
                        key={index}
                        match={match}
                        competitorsMap={competitorsMap}
                    />
                ))}
            </div>
            )}
        </div>
    );
}


const TornLeagueBulkMatchCreateModal = ({
    suggestedMatches,
    tournament,
    onClose,
    onMatchesCreated,
} : {
    suggestedMatches: LeagueSuggestedMatch[];
    tournament: TournamentDetail;
    onClose?: () => void;
    onMatchesCreated?: () => void;
}) => {
    const { popModal } = useModal();
    const { notify } = useNotification();

    const [matchesSuggestions,] = useState<LeagueSuggestedMatch[]>(suggestedMatches);
    const competitorsMap = useMemo(() => {
        return tournament.competitors.reduce((acc, competitor) => {
            acc[competitor.id] = competitor;
            return acc;
        }, {} as Record<string, Competitor>);
    }, [tournament.competitors]);

    const handleClose = () => {
        popModal();
        if (onClose) onClose();
    }

    const handleCreateMatches = () => {
        tournamentsApi.generateMatches(tournament.id, matchesSuggestions)
            .then(() => {
                handleClose();
                if (onMatchesCreated) onMatchesCreated();
            })
            .catch((error: ApiError) => {
                console.error("Error creating matches:", error);
                notify(error.body as string, "error");
            });
    }

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[900px]">
            <h2 className="text-2xl font-bold mb-6">Jogos Sugeridos</h2>

            <div className="space-y-4">
                {Array.from(new Set(matchesSuggestions.map(match => match.format_specific_data.round_number))).map(roundNumber => (
                    <RoundDisplay
                        key={roundNumber}
                        roundNumber={roundNumber}
                        matches={matchesSuggestions}
                        competitorsMap={competitorsMap}
                    />
                ))}
            </div>

            <div className="mt-6 flex space-x-4">
                <Button
                    onClick={handleClose}
                    type="secondary"
                    flexible={true}
                >
                    Cancelar
                </Button>
                <Button
                    onClick={handleCreateMatches}
                    type="primary"
                    flexible={true}
                    disabled={tournament.competitors.length < 2 || matchesSuggestions.length === 0 || tournament.status !== "active"}
                >
                    Criar Jogos
                </Button>
            </div>
        </div>
    );
}

export default TornLeagueBulkMatchCreateModal
