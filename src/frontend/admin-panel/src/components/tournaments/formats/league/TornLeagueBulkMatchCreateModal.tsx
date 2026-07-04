import { useEffect, useState } from "react";
import { tournamentsApi, type TournamentDetail } from "../../../../api/tournaments";

interface LeagueSuggestedMatch {
    competitors: string[];
    round_number: number;
    location?: string;
    time?: string;
}

type Competitor = TournamentDetail["competitors"][0];


const MatchRow = ({
    match,
    competitorsMap,
} : {
    match: LeagueSuggestedMatch,
    competitorsMap: Record<string, Competitor>,
}) => {
    const [localMatch, setLocalMatch] = useState<LeagueSuggestedMatch>(match);
    const [localTime, setLocalTime] = useState<string>(match.time || "");

    const renderCompetitorName = (id: string) => {
        return competitorsMap[id]?.name || id;
    }

    const handleInputChange = (field: keyof LeagueSuggestedMatch, value: string) => {
        if (field === "location" || field === "time") {
            match[field] = value;
        }
    }

    return (
        <div className="items-center space-x-2 grid grid-cols-4">
            <div className="col-span-2 font-semibold">
                {renderCompetitorName(match.competitors[0])} vs {renderCompetitorName(match.competitors[1])}
            </div>

            <input
                type="text"
                value={match.location || ""}
                onChange={(e) => handleInputChange("location", e.target.value)}
                placeholder="Local"
                className="border rounded p-2 flex-1"
            />
            <input
                type="datetime-local"
                value={match.time || ""}
                onChange={(e) => handleInputChange("time", e.target.value)}
                placeholder="Horário"
                className="border rounded p-2 flex-1"
            />
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

    const filteredMatches = matches.filter(match => match.round_number === roundNumber);

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
    tournamentId
} : {
    suggestedMatches: LeagueSuggestedMatch[];
    tournamentId: string;
}) => {

    const [matchesSuggestions,] = useState<LeagueSuggestedMatch[]>(suggestedMatches);
    const [competitorsMap, setCompetitorsMap] = useState<Record<string, Competitor>>({});

    useEffect(() => {
        // Fetch tournament details to get competitors so we can map the id to the name
        tournamentsApi.getById(tournamentId)
            .then((response) => {
                const competitorsMap = response.competitors.reduce((acc, competitor) => {
                    acc[competitor.id] = competitor;
                    return acc;
                }, {} as Record<string, Competitor>);
                setCompetitorsMap(competitorsMap);
            })
            .catch((error) => {
                console.error("Error fetching tournament details:", error);
            });
    }, [tournamentId]);

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[900px]">
            <h2 className="text-2xl font-bold mb-6">Editar Jogos Sugeridos</h2>

            <div className="space-y-4">
                {Array.from(new Set(matchesSuggestions.map(match => match.round_number))).map(roundNumber => (
                    <RoundDisplay
                        key={roundNumber}
                        roundNumber={roundNumber}
                        matches={matchesSuggestions}
                        competitorsMap={competitorsMap}
                    />
                ))}
            </div>
        </div>
    );
}

export default TornLeagueBulkMatchCreateModal
