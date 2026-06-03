import type { TournamentDetail } from "../../api/tournaments";
import ChooseMultipleModal, { type GenericElement } from "../utils/costum_menus/ChoseMultipleModal";
import { teamsApi } from "../../api/teams";
import { tournamentsApi } from "../../api/tournaments";
import { athletesApi } from "../../api/athletes";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";
import { useNotification } from "../../contexts/NotificationProvider";

const TournamentCompetitorsComponent = ({
  tournamentState,
}: {
  tournamentState: [
    TournamentDetail,
    React.Dispatch<React.SetStateAction<TournamentDetail | null>>,
  ];
}) => {
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();
  const { notify } = useNotification();

  const [tournament, setTournament] = tournamentState;

  const getSortedCompetitors = () => {
    if (!tournament.standings || tournament.standings.length === 0) {
      return tournament.competitors;
    }

    // Create a map of competitor_id to position for quick lookup
    const standingsMap = new Map(
      tournament.standings.map((s) => [s.competitor_id, s.position])
    );

    // Sort competitors by their standing position
    return [...tournament.competitors].sort((a, b) => {
      const posA = standingsMap.get(a.id) ?? Infinity;
      const posB = standingsMap.get(b.id) ?? Infinity;
      return posA - posB;
    });
  };

  const getCompetitorPosition = (competitorId: string) => {
    if (!tournament.standings) return null;
    return tournament.standings.find((s) => s.competitor_id === competitorId)?.position;
  };

  const getPodiumBgClass = (position: number | null | undefined) => {
    if (!position) return "bg-gray-50 hover:bg-gray-100";
    switch (position) {
      case 1:
        return "bg-yellow-100 hover:bg-yellow-200 border-2 border-yellow-400";
      case 2:
        return "bg-gray-100 hover:bg-gray-200 border-2 border-gray-400";
      case 3:
        return "bg-orange-100 hover:bg-orange-200 border-2 border-orange-400";
      default:
        return "bg-gray-50 hover:bg-gray-100";
    }
  };

  const handleEditCompetitors = async (chosen: GenericElement[]) => {
    const addedCompetitors = chosen.filter(
      (c) => !tournament.competitors.some((comp) => comp.entity_id === c.id),
    );
    const removedCompetitors = tournament.competitors.filter(
      (comp) => !chosen.some((c) => c.id === comp.entity_id),
    );

    try {
      // Add new competitors
      let updatedTournament: TournamentDetail | null = null;

      if (addedCompetitors.length > 0) {
        await tournamentsApi.addCompetitors(tournament.id, addedCompetitors.map((c) => ({
          competitor_type: tournament.competitor_type,
          entity_id: c.id,
        }))).then((updated) => {
          updatedTournament = updated;
        }).catch((error) => {
          console.error("Error adding competitors:", error);
          notify("Ocorreu um erro ao adicionar competidores. Tente novamente.", "error");
        });
      }

      // Remove old competitors
      if (removedCompetitors.length > 0) {
        await tournamentsApi.removeCompetitors(tournament.id, {
          competitors_ids: removedCompetitors.map((c) => c.id)
        }).then((updated) => {
          updatedTournament = updated;
        }).catch((error) => {
          console.error("Error removing competitors:", error);
          notify("Ocorreu um erro ao remover competidores. Tente novamente.", "error");
        });
      }

      if (updatedTournament) {
        setTournament(updatedTournament);
      }
    } catch (error) {
      console.error("Error updating competitors:", error);
    }
  }

  const loadTeamsForModal = async () => {
    try {
      const teams = await teamsApi.getAll({
        modality_id: tournament.modality.id,
        season_id: tournament.season?.id || undefined,
      });
      return teams.map((team) => ({
        id: team.id,
        title: team.name,
        subTitle: team.course.name,
      }));
    } catch (error) {
      console.error("Error loading teams for modal:", error);
      return [];
    }
  };

  const loadAthletesForModal = async () => {
    try {
      const athletes = await athletesApi.getAll({});
      return athletes.map((athlete) => ({
        id: athlete.id,
        title: athlete.name,
        subTitle: athlete.course.name,
      }));
    } catch (error) {
      console.error("Error loading athletes for modal:", error);
      return [];
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Competidores Inscritos ({tournament.competitors.length})
        </h2>
        <Button
          onClick={() => pushModal(
            <ChooseMultipleModal
              allElementsLoader={() => tournament.competitor_type === "team" ? loadTeamsForModal() : loadAthletesForModal()}
              initialChosenElementsIds={tournament.competitors.map(
                (c) => c.entity_id,
              )}
              onSave={handleEditCompetitors}
              title="Selecionar Competidores do Torneio"
              showSummary={true}
            />
          )}
          type="primary"
          active={isAdminGeneral}
        >
          +/- Editar Competidor
        </Button>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {tournament.competitors.length > 0 ? (
          getSortedCompetitors().map((competitor) => {
            const position = getCompetitorPosition(competitor.id);
            return (
              <div
                key={`${competitor.id}`}
                className={`flex justify-between items-center p-4 rounded-md transition-colors ${getPodiumBgClass(position)}`}
              >
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-800">{competitor.name}</p>
                </div>
                <p className="text-sm text-gray-600">
                  {competitor.course_name}
                </p>
              </div>
              {position && (
                <span className="font-bold text-xl min-w-10 h-10 flex items-center justify-center rounded-full text-white" style={{
                  backgroundColor: position === 1 ? '#FFD700' : position === 2 ? '#C0C0C0' : position === 3 ? '#CD7F32' : '#ccc',
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}>
                  {position}
                </span>
              )}
              {/* <button
                    onClick={() =>
                      handleRemoveCompetitor(competitor, name || "Desconhecido")
                    }
                    className={`px-3 py-1 ${btn.dangerLight} rounded-md text-sm transition-colors`}
                  >
                    Remover
                  </button> */}
            </div>
            );
          })
        ) : (
          <p className="text-gray-500 text-center py-8">
            Nenhum competidor inscrito
          </p>
        )}
      </div>
    </div>
  );
};

export default TournamentCompetitorsComponent;
