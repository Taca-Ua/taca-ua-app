import { useEffect, useState } from "react";
import { teamsApi, type TeamDetail } from "../../api/teams";
import HelpTooltip from "../HelpTooltip";
import { btn } from "../../styles/buttonStyles";
import { useNotification } from "../../contexts/NotificationProvider";

const TeamEditModel = ({
  controller,
  onSave,
  teamData,
  teamId,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onSave: (updatedTeam: TeamDetail) => void;
  teamData?: TeamDetail;
  teamId?: string;
}) => {
  if (!teamId && !teamData) {
    throw new Error("TeamEditModel requires either teamId or teamData");
  }

  teamId = teamId || teamData!.id; // Use the provided teamId or extract it from teamData

  const { notify } = useNotification();
  const [isOpen, setIsOpen] = controller;

  const [editedName, setEditedName] = useState("");

  useEffect(() => {
    if (teamData) {
      setEditedName(teamData.name);
    }

    const fetchTeam = async () => {
      try {
        const data = await teamsApi.get(teamId!);
        setEditedName(data.name);
      } catch (error) {
        console.error("Error fetching team data:", error);
        notify(
          "Não foi possível carregar os dados da equipa. Tente novamente.",
          "error",
        );
        setIsOpen(false); // Close the modal if team data cannot be loaded
      }
    };

    fetchTeam();
  }, [teamId]);

  const onClose = () => {
    setEditedName(teamData ? teamData.name : ""); // Reset to original name on close
    setIsOpen(false);
  };

  const handleSave = async () => {
    if (!editedName.trim()) {
      notify("Por favor, preencha o nome da equipa.", "error");
      return;
    }

    try {
      const teamData = await teamsApi.update(teamId, {
        name: editedName,
      });

      onSave(teamData);

      onClose();
    } catch (err) {
      console.error("Error updating team:", err);
      notify(
        "Não foi possível guardar as alterações à equipa. Tente novamente.",
        "error",
      );
    }
  };

  if (!isOpen) {
    return null; // Don't render the modal if it's not open
  }

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
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium transition-colors`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeamEditModel;
