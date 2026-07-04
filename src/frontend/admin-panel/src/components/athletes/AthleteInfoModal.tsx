import { type AthleteDetail, athletesApi } from "../../api/athletes"
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import AthleteEditModal from "./AthleteEditModal";
import { useModal } from "../../contexts/ModalContext";
import { useEffect, useState } from "react";


const showFileButton = (fileUrl: string | undefined, label: string) => {
    if (!fileUrl) {
        return <span className="text-gray-500">Não fornecido</span>;
    }

    return (
      <a
        href={fileUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-2"
      >
        <div className="flex items-center gap-2 bg-blue-500 p-2 rounded-lg text-white hover:bg-blue-600 transition-colors">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          {label}
        </div>
      </a>
    );
}

const AthleteInfoModal = ( {
    athleteId,
    onEditSave,
    onDelete,
} : {
    athleteId: string,
    onEditSave?: (updated: AthleteDetail) => void
    onDelete?: () => void
} ) => {
    const [athlete, setAthlete] = useState<AthleteDetail | null>(null);
    const { notify } = useNotification();
    const { popModal, pushModal } = useModal();

    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        setIsLoading(true);
        athletesApi.getById(athleteId)
            .then((data) => {
                setAthlete(data);
            })
            .catch((err) => {
                console.error("Failed to fetch athlete details:", err);
                notify("Erro ao carregar detalhes do atleta. Tente novamente.", "error");
                popModal();
            })
            .finally(() => {
                setIsLoading(false);
            });
    }, [athleteId]);

    const onClose = () => {
        popModal();
    };

    const handleDelete = () => {
        if (!athlete) return;
        athletesApi.delete(athlete.id)
            .then(() => {
                notify("Atleta eliminado com sucesso.", "success");
                setAthlete(null);
                if (onDelete) onDelete();
                onClose();
            })
            .catch((err) => {
                console.error("Failed to delete athlete:", err);
                notify("Erro ao eliminar atleta. Tente novamente.", "error");
            });
    };

    if (isLoading) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
                <p className="text-gray-500 text-center">Carregando detalhes do atleta...</p>
            </div>
        );
    }

    if (!athlete) return null;

    return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <span className="inline-block px-4 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                Participante
              </span>
              <h2 className="text-2xl font-bold text-gray-800">
                {athlete.name}
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

            <div className="flex justify-between items-center mb-2">
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Prova de Curso
                </label>
                {showFileButton(athlete.course_proof_file_url, "Ver Prova de Curso")}
              </div>

              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Prova de Pagamento
                </label>
                {showFileButton(athlete.payment_proof_file_url, "Ver Prova de Pagamento")}
              </div>
            </div>
          </div>

          <div className="flex gap-4 mt-4">
            <Button onClick={onClose} type="secondary" flexible={true}>
              Fechar
            </Button>
            <Button
              onClick={() => pushModal(
                <AthleteEditModal
                  athleteState={[athlete, setAthlete]}
                  onSave={(updated) => {
                    setAthlete(updated);
                    if (onEditSave) onEditSave(updated);
                  }}
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
    );
}

export default AthleteInfoModal;
