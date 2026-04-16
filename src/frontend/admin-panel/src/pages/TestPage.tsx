import { useEffect, useState } from "react";
import { type TournamentDetail, tournamentsApi } from "../api/tournaments";
import TournamentFinishModal from "../components/tournaments/TournamentFinishModal";
import TournamentInfoComponent from "../components/tournaments/TournamentInfoComponent";
import { useNotification } from "../contexts/NotificationProvider";
import MatchesListComponent from "../components/matches/MatchesListComponent";
import MatchCreateModal from "../components/matches/MatchCreateModal";

const TestPage = () => {

    const [tournament, setTournament] = useState<TournamentDetail | null>( null );

    useEffect(() => {
        const fetchTournament = async () => {
            try {
                const data = await tournamentsApi.getById("4cf87fe9-9209-4013-8aed-ccf97a7439cf");
                setTournament(data);
            } catch (error) {
                console.error("Error fetching tournament:", error);
            }
        };

        fetchTournament();
    }, []);

    if (!tournament) {
        return <div>Loading...</div>;
    }

    return (
        <div className="p-4 bg-black text-white min-h-screen">
            <h1 className="text-2xl font-bold mb-4">Página de Teste</h1>
            <MatchesListComponent tournamentId={"4cf87fe9-9209-4013-8aed-ccf97a7439cf"} />
            <MatchCreateModal
                controller={[true, () => {}]}
                tournament={tournament}
            />
        </div>
    )
}

export default TestPage
