import { useModal } from "../../contexts/ModalContext";
import { matchesApi, type MatchDetail, type MatchLineup } from "../../api/matches";
import ChooseMultipleModal from "../utils/costum_menus/ChoseMultipleModal";
import { athletesApi } from "../../api/athletes";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";

const MatchTeamLineupModal = ( {
    match,
    lineup,
} : {
    match: MatchDetail
    lineup: MatchLineup;
} ) => {
    const { popModal, pushModal } = useModal();
    const { notify } = useNotification();
    // console.log("MatchTeamLineupModal lineup:", lineup);
    // console.log("MatchTeamLineupModal match:", match);

    const onClose = () => {
        popModal();
    }

    const handleEditLineup = () => {
        matchesApi.assignLineup(match.id, {
            participant: lineup.participant_id,
            players: lineup.lineup.map(player => ({
                player: player.player_id,
                is_starter: player.is_starter,
                jersey_number: player.jersey_number,
            }))
        }).then(() => {
            // Optionally, you can show a success message or refresh the data
            notify("Lineup updated successfully", "success");
        }).catch((error) => {
            // Handle error case
            notify("Error updating lineup", "error");
            console.error("Error updating lineup:", error);
        });
    };

    return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[700px]">
        <div>
            <h2 className="text-2xl font-bold mb-4">
            Lineup for Participant {lineup.participant_id}
            </h2>
            <Button
                onClick={() => {pushModal(
                    <ChooseMultipleModal
                        allElementsLoader={ () =>
                            athletesApi.getAll().then(res => res.map(athlete => ({
                                id: athlete.id,
                                title: athlete.full_name,
                                subTitle: `ID: ${athlete.id}`,
                            })))
                        }
                        initialChosenElementsIds={lineup.lineup.map(player => player.player_id)}
                        onSave={ (selectedIds) => {
                          console.log("Selected player IDs:", selectedIds.map(player_id => (player_id.id)));
                            matchesApi.assignLineup(match.id, {
                                participant: lineup.participant_id,
                                players: selectedIds.map(player_id => (player_id.id)),
                            }).then(() => {
                                notify("Lineup updated successfully", "success");
                                console.log("Lineup updated successfully");
                            }).catch((error) => {
                                notify("Error updating lineup", "error");
                                console.error("Error updating lineup:", error);
                            });
                        }}
                        showSummary={true}
                    />
                )}}
            >
                Edit Lineup
            </Button>
        </div>
        <ul className="divide-y divide-gray-200">
          {lineup.lineup.map((player) => (
            <li
              key={player.player_id}
              className="py-4 flex items-center justify-between"
            >
              <div>
                <p className="text-lg font-medium">{player.name}</p>
                <p className="text-sm text-gray-500">
                  Player ID: {player.player_id}
                </p>
              </div>
              <div className="flex items-center space-x-4">
                {player.jersey_number && (
                  <span className="text-sm text-gray-500">
                    #{player.jersey_number}
                  </span>
                )}
                {player.is_starter ? (
                  <span className="text-green-600 font-semibold">Starter</span>
                ) : (
                  <span className="text-gray-600 font-semibold">
                    Substitute
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
        <button
          onClick={onClose}
          className="mt-6 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          Close
        </button>
      </div>
    );
}

export default MatchTeamLineupModal;
