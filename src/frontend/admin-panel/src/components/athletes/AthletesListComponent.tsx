import { type AthleteListItem, athletesApi } from "../../api/athletes";
import { useState } from "react";
import { useNotification } from "../../contexts/NotificationProvider";
import AthleteInfoModal from "./AthleteInfoModal";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";

const AthletesListBanner = ({
  athleteData,
  onDelete,
}: {
  athleteData: AthleteListItem
  onDelete?: () => void
}) => {

    const { notify } = useNotification();
    const { pushModal } = useModal();
    const { isAdminGeneral } = useAuth();

    const [isloading, setIsLoading] = useState(false);
    const [athlete, setAthlete] = useState(athleteData);

    const onToggle = () => {
        setIsLoading(true);
        athletesApi.update(athlete.id, {
            is_member: !athlete.is_member,
        }).then(updated => {
            setAthlete(prev => prev ? { ...prev, is_member: updated.is_member } : prev);
            notify(`Sócio ${updated.is_member ? "ativado" : "desativado"} para ${updated.full_name}.`);
        }).catch(err => {
            console.error("Failed to update athlete:", err);
            notify("Erro ao atualizar sócio. Tente novamente.");
        }).finally(() => {
            setIsLoading(false);
        });
    }

    return (
      <li
        key={athlete.id}
        className="px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-gray-50"
      >
        <div
          className="min-w-0 flex-1"
          onClick={() => pushModal(
            <AthleteInfoModal
              athleteId={athlete.id}
              onEditSave={(updated) => setAthlete(updated)}
              onDelete={() => {
                if (onDelete) onDelete();
              }}
            />
          )}
        >
          <p className="font-medium text-teal-700">{athlete.full_name}</p>

          <div className="text-sm text-gray-600 mt-0.5">
            NMEC {athlete.student_number}
            {athlete.course?.name ? ` · ${athlete.course.name}` : ""}
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <span className="text-sm text-gray-600 w-24 text-right sm:text-left">
            {athlete.is_member ? "Sócio" : "Não sócio"}
          </span>
          {isAdminGeneral && (<button
            type="button"
            role="switch"
            aria-checked={athlete.is_member}
            disabled={isloading}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggle();
            }}
            className={`
                relative inline-flex h-8 w-14 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors
                focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2
                ${isloading ? "opacity-50 cursor-not-allowed" : ""}
                ${athlete.is_member ? "bg-teal-600" : "bg-gray-200"}
            `}
          >
            <span
              className={`
                pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition
                ${athlete.is_member ? "translate-x-6" : "translate-x-0.5"}
              `}
            />
          </button>)}
        </div>
      </li>
    );
};

const AthletesListComponent = ( {
    athletesState,
} : {
    athletesState: [AthleteListItem[] | null, React.Dispatch<React.SetStateAction<AthleteListItem[] | null>>]
} ) => {

    const [athletes, setAthletes] = athletesState;

    if (athletes === null) {
        return (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 animate-spin text-gray-400"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p className="mt-2 text-sm text-gray-500">Carregando atletas...</p>
          </div>
        );
    }

    if (athletes.length === 0) {
        return (
          <div className="text-center py-12 text-gray-500">
            Nenhum participante corresponde aos filtros.
          </div>
        );
    }

    return (
      <ul className="divide-y divide-gray-100 max-h-[640px] overflow-y-auto">
        {athletes
          .sort((a, b) => a.full_name.localeCompare(b.full_name))
          .map((athlete) => (
            <AthletesListBanner
              key={athlete.id}
              athleteData={athlete}
              onDelete={() => {
                setAthletes((prev) => prev ? prev.filter((a) => a.id !== athlete.id) : null);
              }}
            />
          ))}
      </ul>
    );
}

export default AthletesListComponent;
