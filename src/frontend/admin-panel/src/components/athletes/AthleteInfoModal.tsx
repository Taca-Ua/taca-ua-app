import { useState } from "react";
import { type AthleteDetail, athletesApi } from "../../api/athletes"
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import AthleteEditModal from "./AthleteEditModal";

const AthleteInfoModal = ( {
    controller,
    athleteState,
    onEditSave,
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>]
    athleteState: [AthleteDetail, React.Dispatch<React.SetStateAction<AthleteDetail | null>>]
    onEditSave?: (updated: AthleteDetail) => void
} ) => {
    const [isOpen, setIsOpen] = controller;
    const [athlete, setAthlete] = athleteState;
    const { notify } = useNotification();

    const [isEditModalOpen, setIsEditModalOpen] = useState(false);

    const onClose = () => {
        setIsOpen(false);
    };

    const handleDelete = () => {
        athletesApi.delete(athlete.id)
            .then(() => {
                notify("Atleta eliminado com sucesso.", "success");
                setAthlete(null);
                onClose();
            })
            .catch((err) => {
                console.error("Failed to delete athlete:", err);
                notify("Erro ao eliminar atleta. Tente novamente.", "error");
            });
    };

    if (!isOpen) return null;

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <span className="inline-block px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                Participante
              </span>
              <h2 className="text-2xl font-bold text-gray-800">
                {athlete.full_name}
              </h2>
            </div>

            <div>
              <label className="block text-teal-500 font-medium mb-2">
                Número de Estudante
              </label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {athlete.student_number}
              </div>
            </div>

            <div>
              <label className="block text-teal-500 font-medium mb-2">
                Estado de Membro
              </label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md">
                <span
                  className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    athlete.is_member
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {athlete.is_member ? "Membro" : "Não-Membro"}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-teal-500 font-medium mb-2">
                Curso
              </label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {athlete.course.name}
              </div>
            </div>
          </div>

          <div className="flex gap-4 mt-4">
            <Button onClick={onClose} type="secondary" flexible={true}>
              Fechar
            </Button>
            <Button
              onClick={() => setIsEditModalOpen(true)}
              type="primary"
              flexible={true}
            >
              Editar
            </Button>
            <Button
              onClick={handleDelete}
              type="danger"
              flexible={true}
              confirmation={{
                title: "Tem certeza que deseja eliminar este atleta?",
                message: "Esta ação é irreversível.",
                confirmLabel: "Sim, eliminar",
              }}
            >
              Eliminar
            </Button>
          </div>
        </div>
        <AthleteEditModal
          controller={[isEditModalOpen, setIsEditModalOpen]}
          athleteState={[athlete, setAthlete]}
          onSave={(updated) => {
            setAthlete(updated);
            if (onEditSave) onEditSave(updated);
          }}
        />
      </div>
    );
}

export default AthleteInfoModal;
