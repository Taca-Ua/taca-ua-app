import type { TournamentDetail } from "../../api/tournaments";
import ChooseMultipleModal, { type GenericElement } from "../utils/costum_menus/ChoseMultipleModal";
import { teamsApi } from "../../api/teams";
import { tournamentsApi } from "../../api/tournaments";
import { athletesApi } from "../../api/athletes";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";

const TournamentCompetitorsComponent = ({
  tournamentState,
}: {
  tournamentState: [
    TournamentDetail,
    React.Dispatch<React.SetStateAction<TournamentDetail | null>>,
  ];
}) => {
  const { pushModal } = useModal();

  const [tournament, setTournament] = tournamentState;

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

      await tournamentsApi.addCompetitors(tournament.id, addedCompetitors.map((c) => ({
        competitor_type: tournament.competitor_type,
        entity_id: c.id,
      }))).then((updated) => {
        updatedTournament = updated;
      }).catch((error) => {
        console.error("Error adding competitors:", error);
      });

      // Remove old competitors
      await tournamentsApi.removeCompetitors(tournament.id, {
        competitors_ids: removedCompetitors.map((c) => c.id)
      }).then((updated) => {
        updatedTournament = updated;
      }).catch((error) => {
        console.error("Error removing competitors:", error);
      });

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
        title: athlete.full_name,
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
        >
          +/- Editar Competidor
        </Button>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {tournament.competitors.length > 0 ? (
          tournament.competitors.map((competitor) => {
            return (
              <div
                key={`${competitor.id}`}
                className="flex justify-between items-center p-4 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
              >
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-800">{competitor.name}</p>
                </div>
                <p className="text-sm text-gray-600">
                  {competitor.course_name}
                </p>
              </div>
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
        })) : (
          <p className="text-gray-500 text-center py-8">
            Nenhum competidor inscrito
          </p>
        )}
      </div>
    </div>
  );
};

export default TournamentCompetitorsComponent;
