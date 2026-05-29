import HelpTooltip from "../HelpTooltip";
import { type CourseDetail, coursesApi } from "../../api/courses";
import CourseEditModal from "./CourseEditModal";
import { useAuth } from "../../hooks/useAuth";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useSeason } from "../../contexts/SeasonContext";
import { useNotification } from "../../contexts/NotificationProvider";
import LazyImage from "../utils/LazyImage";

const CourseInfoComponent = ( {
  courseState,
} : {
  courseState: [CourseDetail | null, React.Dispatch<React.SetStateAction<CourseDetail | null>>],
}) => {
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();
  const { loadedSeason } = useSeason();
  const { notify } = useNotification();

  const [course, setCourse] = courseState;

  const handleRemoveFromSeason = () => {
    if (!course || !loadedSeason) return;
    coursesApi.removeFromSeason(course.id, loadedSeason.id)
      .then((updatedCourse) => {
        setCourse(updatedCourse);
      }).catch((error) => {
        notify("Erro ao remover curso da temporada.", "error");
        console.error("Erro ao remover curso da temporada:", error);
      });
  };

  const handleAddToSeason = () => {
    if (!course || !loadedSeason) return;
    coursesApi.addToSeason(course.id, loadedSeason.id)
      .then((updatedCourse) => {
        setCourse(updatedCourse);
      }).catch((error) => {
        notify("Erro ao adicionar curso à temporada.", "error");
        console.error("Erro ao adicionar curso à temporada:", error);
      });
  };

  if (!course) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-red-500">Curso não encontrado.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div className="flex items-center gap-6">
        <div>
          {course.logo_url ? (
            <div className="flex items-center gap-4">
              <LazyImage
                src={course.logo_url}
                alt={course.name}
                className="w-64 h-64 object-cover"
              />
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <div className="w-64 h-64 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
                <span className="text-teal-600 font-bold text-4xl">
                  {course.abbreviation}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="ml-8 flex-1 space-y-4">
          <div>
            <label className="block text-teal-500 font-medium mb-2">Nome</label>
            <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
              {course.name}
            </div>
          </div>
          <div>
            <label className="block text-teal-500 font-medium mb-2">
              Abreviatura{" "}
              <HelpTooltip
                text="Código curto do curso, ex: MECT, LEI, LECI. Utilizado como identificador visual no sistema."
                className="ml-1"
              />
            </label>
            <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
              {course.abbreviation}
            </div>
          </div>

          <div>
            <label className="block text-teal-500 font-medium mb-2">
              Núcleo{" "}
              <HelpTooltip
                text="Associação académica (núcleo) a que este curso pertence."
                className="ml-1"
              />
            </label>
            <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
              {course.nucleo.name}
            </div>
          </div>
        </div>

      </div>

      <div className="flex gap-4 pt-4">
        <Button
          onClick={() =>
            pushModal(<CourseEditModal courseState={[course, setCourse]} />)
          }
          type="primary"
          active={isAdminGeneral}
          flexible={true}
        >
          Editar
        </Button>
        <Button
          onClick={handleAddToSeason}
          type="info"
          active={isAdminGeneral && !course.belongs_to_season}
          confirmation={{
            title: "Adicionar curso à temporada",
            message: `Tem certeza que deseja adicionar "${course.name}" à temporada "${loadedSeason?.name}"?`,
            confirmLabel: "Adicionar",
            cancelLabel: "Cancelar",
          }}
          flexible={true}
        >
          Adicionar à temporada
        </Button>
        <Button
          onClick={handleRemoveFromSeason}
          type="danger"
          active={isAdminGeneral && course.belongs_to_season}
          confirmation={{
            title: "Remover curso",
            message: `Tem certeza que deseja remover "${course.name}" da temporada "${loadedSeason?.name}"? Esta ação não pode ser desfeita.`,
            confirmLabel: "Remover",
            cancelLabel: "Cancelar",
          }}
          flexible={true}
        >
          Remover da temporada
        </Button>
      </div>
    </div>
  );
};

export default CourseInfoComponent;
