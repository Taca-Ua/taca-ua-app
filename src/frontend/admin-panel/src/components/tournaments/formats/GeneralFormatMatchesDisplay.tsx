import { useEffect, useState } from "react";
import { matchesApi, type MatchListItem } from "../../../api/matches"
import { type TournamentDetail } from "../../../api/tournaments"
import TornLeagueMatchesDisplay from "./league/TornLeagueMatchesDisplay";
import Button from "../../utils/Button";
import MatchCreateModal from "../../matches/MatchCreateModal";
import MatchesListComponent from "../../matches/MatchesListComponent";
import { useModal } from "../../../contexts/ModalContext";
import { useAuth } from "../../../hooks/useAuth";

const GeneralFormatMatchesDisplay = ({
    tournament
} : {
    tournament: TournamentDetail
}) => {
    const { pushModal } = useModal();
    const { isAdminGeneral } = useAuth();

    const [matches, setMatches] = useState<MatchListItem[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        setLoading(true);
        matchesApi.getAll({ tournament_id: tournament.id })
            .then((response) => {
                setMatches(response.matches);
            })
            .catch((error) => {
                console.error("Error fetching matches:", error);
            }).finally(() => {
                setLoading(false);
            });
    }, [tournament.id]);

    if (loading) {
        return <p>Carregando jogos...</p>;
    }

    if (!matches) {
        return <p className="text-red-500">Erro ao carregar os jogos.</p>;
    }

    switch (tournament.format) {
        case "league":
            return (<TornLeagueMatchesDisplay tournament={tournament} matchesState={[matches, setMatches]} />);
        default:
            return (
              <>
                <Button
                  onClick={() =>
                    pushModal(
                      <MatchCreateModal
                        tournament={tournament}
                        onCreated={(newMatch) => {
                          setMatches((prev) => [...prev, newMatch]);
                        }}
                      />,
                    )
                  }
                  active={isAdminGeneral && tournament.competitors.length >= 2}
                  flexible={true}
                >
                  + Criar Jogo
                </Button>
                <MatchesListComponent
                  tournamentId={tournament.id}
                  matchesState={[matches, setMatches]}
                />
              </>
            );
    }
}

export default GeneralFormatMatchesDisplay
