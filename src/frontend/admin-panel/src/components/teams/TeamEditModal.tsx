import { useEffect, useState } from "react";
import { teamsApi, type TeamDetail } from "../../api/teams";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";

const TeamEditModal = ({
  teamState,
  onSave,
}: {
  teamState: [TeamDetail, React.Dispatch<React.SetStateAction<TeamDetail | null>>];
  onSave?: (updatedTeam: TeamDetail) => void;
}) => {

  const [teamData, setTeamData] = teamState;
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [editedName, setEditedName] = useState(teamData.name);

  useEffect(() => {
    setEditedName(teamData.name);
  }, [teamData]);

  const onClose = () => {
    setEditedName(teamData.name); // Reset to original name on close
    popModal();
  };

  const handleSave = async () => {
    if (!editedName.trim()) {
      notify("Por favor, preencha o nome da equipa.", "error");
      return;
    }

    teamsApi.update(teamData.id, {
      name: editedName,
    }).then((updatedTeam) => {
      setTeamData(updatedTeam);
      if (onSave) onSave(updatedTeam);
      onClose();
      notify("Equipa atualizada com sucesso!", "success");
    }).catch((err) => {
      console.error("Error updating team:", err);
      notify("Não foi possível guardar as alterações à equipa. Tente novamente.", "error");
    });
  };

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Equipa</h2>

        <div className="space-y-4">
          <div>
            <label
              htmlFor="editName"
              className="block text-gray-700 font-medium mb-2"
            >
              Nome da Equipa{" "}
              <HelpTooltip
                text="Nome pelo qual a equipa é identificada nos torneios e rankings. Deve ser único dentro do núcleo."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="editName"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Digite o nome da equipa"
            />
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button
            onClick={onClose}
            type="secondary"
            flexible={true}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSave}
            type="primary"
            flexible={true}
          >
            Guardar
          </Button>
        </div>
      </div>
  );
};

export default TeamEditModal;
