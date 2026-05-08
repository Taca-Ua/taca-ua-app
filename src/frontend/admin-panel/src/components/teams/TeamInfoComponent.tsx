import { useEffect, useState } from "react";
import { teamsApi, type TeamDetail } from "../../api/teams";
import HelpTooltip from "../HelpTooltip";
import TeamEditModal from "./TeamEditModal";
import ChooseMultipleModal, {
  type GenericElement,
} from "../utils/costum_menus/ChoseMultipleModal";
import { athletesApi, type AthleteListItem } from "../../api/athletes";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useNotification } from "../../contexts/NotificationProvider";
import { useNavigate } from "react-router-dom";

const TeamDetailComponent = ({
  teamState
} : {
  teamState: [TeamDetail | null, React.Dispatch<React.SetStateAction<TeamDetail | null>>]
}) => {
  const [team, setTeam] = teamState;
  const { pushModal } = useModal();
  const { notify } = useNotification();
  const navigate = useNavigate();

  const [avaiblePlayers, setAvailablePlayers] = useState<AthleteListItem[]>([]);

  useEffect(() => {
    const fetchAvailablePlayers = async () => {
      try {
        const data = await athletesApi.getAll();
        setAvailablePlayers(data);
      } catch (error) {
        console.error("Error fetching available players:", error);
      }
    };

    fetchAvailablePlayers();
  }, []);

  const handleDelete = async () => {
    if (!team) return;
    teamsApi.delete(team.id)
      .then(() => {
        notify("Equipa eliminada com sucesso.", "success");
        navigate("/equipas");
      })
      .catch((error) => {
        console.error("Error deleting team:", error);
        notify("Erro ao eliminar a equipa.", "error");
      });
  };

  const handleUpdatePlayers = async (players: GenericElement[]) => {
    if (!team) return;
    const playersToAdd = players.filter(
      (p) => !team?.players.some((tp) => tp.id === p.id),
    );
    const playersToRemove =
      team?.players.filter((tp) => !players.some((p) => p.id === tp.id)) || [];

    try {
      const updatedTeam = await teamsApi.update(team.id, {
        players_add: playersToAdd.map((p) => p.id),
        players_remove: playersToRemove.map((p) => p.id),
      });
      setTeam(updatedTeam);
    } catch (error) {
      console.error("Error updating team players:", error);
    }
  };

  if (!team) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Equipa não encontrada.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

      {/* Detalhes da Equipa */}
      <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Imagem da Equipa */}
        <div className="flex justify-center mb-8">
          <div className="w-48 h-48 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
            <svg
              className="w-24 h-24 text-gray-700"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </div>
        </div>

        {/* Nome da Equipa */}
        <div>
          <label className="block text-teal-500 font-medium mb-2">Nome</label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
            {team.name}
          </div>
        </div>

        {/* Modalidade */}
        <div>
          <label className="block text-teal-500 font-medium mb-2">
            Modalidade{" "}
            <HelpTooltip
              text="Desporto desta equipa. Define os torneios em que pode participar."
              className="ml-1"
            />
          </label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
            {team.modality.name}
          </div>
        </div>

        {/* Curso */}
        <div>
          <label className="block text-teal-500 font-medium mb-2">
            Curso{" "}
            <HelpTooltip
              text="Curso académico que esta equipa representa."
              className="ml-1"
            />
          </label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
            {team.course.name}
          </div>
        </div>

        {/* Número de Jogadores */}
        <div>
          <label className="block text-teal-500 font-medium mb-2">
            Número de Jogadores
          </label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
            {team.players.length}
          </div>
        </div>

        {/* Ações */}
        <div className="flex gap-4 mt-6">
          <Button
            onClick={() => pushModal(
              <TeamEditModal
                teamState={[team, setTeam]}
              />
            )}
            type="primary"
            flexible={true}
          >
            Editar
          </Button>
          <Button
            onClick={handleDelete}
            type="danger"
            confirmation={{
              title: "Eliminar equipa",
              message: `Tem certeza que deseja eliminar a equipa "${team.name}"? Esta ação não pode ser desfeita.`,
              confirmLabel: "Eliminar",
            }}
            flexible={true}
          >
            Eliminar
          </Button>
        </div>
      </div>

      {/* Membros da Equipa */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Equipa</h2>
          <div>
            <Button
              onClick={() => pushModal(
                <ChooseMultipleModal
                  allElementsLoader={() => Promise.resolve(avaiblePlayers.map((player) => ({
                    id: player.id,
                    title: player.full_name,
                    subTitle: `NMEC: ${player.student_number}`,
                  })))}
                  initialChosenElementsIds={team.players.map((ele) => ele.id)}
                  onSave={(chosenElements) => handleUpdatePlayers(chosenElements)}
                  title="Selecionar Membros da Equipa"
                />
              )}
              type="primary"
            >
              +/- Editar Membros
            </Button>
          </div>
        </div>

        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {team.players.length > 0 ? (
            team.players.map((member) => (
            <div
                key={member.id}
                className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                    <span className="text-teal-700 font-medium">
                      {member.full_name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-gray-800 font-medium">{member.full_name}</p>
                  </div>
                  <div className="ml-4 px-2 py-1 bg-gray-200 rounded text-sm text-gray-600">
                    NMEC: {member.student_number}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">
              Nenhum membro na equipa.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamDetailComponent;
