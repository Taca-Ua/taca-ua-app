import { useEffect, useState } from "react";
import { type TournamentDetail, tournamentsApi } from "../api/tournaments";
import { type AdminDetail, administratorsApi } from "../api/admins";
import AdminEditModal from "../components/admins/AdminEditModal";

const TestPage = () => {

    const [tournament, setTournament] = useState<TournamentDetail | null>( null );
    const [admin, setAdmin] = useState<AdminDetail | null>( null );

    useEffect(() => {
        const fetchTournament = async () => {
            try {
                const data = await tournamentsApi.getById("4cf87fe9-9209-4013-8aed-ccf97a7439cf");
                setTournament(data);
            } catch (error) {
                console.error("Error fetching tournament:", error);
            }
        };

        const fetchAdmin = async () => {
            try {
                // const data = await administratorsApi.getById("da8d9f7d-2513-43d1-92cb-f8502da8e71c");
                const data = await administratorsApi.getById("3d1c7c87-de40-4828-9f3b-970e81648505");
                setAdmin(data);
            } catch (error) {
                console.error("Error fetching admin:", error);
            }
        };


        // fetchTournament();
        fetchAdmin();
    }, []);

    // if (!tournament) {
    //     return <div>Loading...</div>;
    // }

    if (!admin) {
        return <div>Loading...</div>;
    }

    return (
        <div className="p-4 bg-black text-white min-h-screen">
            <h1 className="text-2xl font-bold mb-4">Página de Teste</h1>
            {/* <MatchesListComponent tournamentId={"4cf87fe9-9209-4013-8aed-ccf97a7439cf"} />
            <MatchCreateModal
                controller={[true, () => {}]}
                tournament={tournament}
            /> */}
            <AdminEditModal
                controller={[true, () => {}]}
                adminState={[admin, setAdmin]}
                onSaved={() => console.log("Fechar modal")}
            />
        </div>
    )
}

export default TestPage
