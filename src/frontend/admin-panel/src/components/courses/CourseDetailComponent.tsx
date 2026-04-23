import { useEffect, useState } from "react";
import HelpTooltip from "../HelpTooltip";
import { type CourseDetail, coursesApi } from "../../api/courses";
import CourseEditModal from "./CourseEditModal";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";

const CourseDetailComponent = ( {courseId} : { courseId: string } ) => {
  const navigate = useNavigate();
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const handleDelete = async () => {
    try {
      await coursesApi.delete(courseId);
      navigate('/geral/cursos');
    } catch (error) {
      console.error("Erro ao eliminar curso:", error);
    } finally {
    }
  };

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const data = await coursesApi.getById(courseId);
        setCourse(data);
      } catch (error) {
        console.error("Erro ao carregar detalhes do curso:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [courseId]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500">Carregando detalhes do curso...</p>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-red-500">Curso não encontrado.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div>
        <label className="block text-teal-500 font-medium mb-2">Logo</label>
        <div className="flex items-center gap-4">
          <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
            <span className="text-teal-600 font-bold text-2xl">
              {course.abbreviation}
            </span>
          </div>
        </div>
      </div>

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

      <div className="flex gap-4 pt-4">
        <Button
          onClick={() => pushModal(<CourseEditModal courseState={[course, setCourse]} />)}
          type="primary"
          active={isAdminGeneral}
          flexible={true}
        >
          Editar
        </Button>
        <Button
          onClick={handleDelete}
          type="danger"
          active={isAdminGeneral}
          confirmation={{
            title: "Eliminar curso",
            message: `Tem certeza que deseja eliminar "${course.name}"? Esta ação não pode ser desfeita.`,
            confirmLabel: "Eliminar",
            cancelLabel: "Cancelar",
          }}
          flexible={true}
        >
          Eliminar
        </Button>
      </div>
    </div>
  );
};

export default CourseDetailComponent;
