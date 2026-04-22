import { useEffect, useState } from "react";
import { teamsApi, type TeamDetail } from "../../api/teams";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";

const TeamEditModal = ({
  controller,
  teamState,
  onSave,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  teamState: [TeamDetail, React.Dispatch<React.SetStateAction<TeamDetail | null>>];
  onSave?: (updatedTeam: TeamDetail) => void;
}) => {

  const [isOpen, setIsOpen] = controller;
  const [teamData, setTeamData] = teamState;
  const { notify } = useNotification();

  const [editedName, setEditedName] = useState(teamData.name);

  useEffect(() => {
    if (!isOpen) return;
    setEditedName(teamData.name);
  }, [isOpen, teamData]);

  const onClose = () => {
    setEditedName(teamData.name); // Reset to original name on close
    setIsOpen(false);
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
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
    </div>
  );
};

export default TeamEditModal;
