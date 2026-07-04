import { useEffect, useState } from "react";
import LineupsSection from "../components/matches/MatchLineupComponent";
import { type MatchDetail, matchesApi } from "../api/matches";

const TestPage = () => {

    const [match, setMatch] = useState<MatchDetail | null>(null);

    useEffect(() => {
        matchesApi.getById('3ca142ed-9a65-40e9-8def-0adce8a5d9a4').then(setMatch).catch(console.error);
    }, []);

    if (match === null) {
        return (
            <div className="flex items-center justify-center h-screen">
                <p className="text-gray-600">Carregando dados do jogo...</p>
            </div>
        );
    }
    return (
        <div className="w-2/3">
            <LineupsSection match={match} />
        </div>
    );
};

export default TestPage;
