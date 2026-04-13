import { useEffect, useState } from "react";
import HelpTooltip from "../HelpTooltip";
import { btn } from "../../styles/buttonStyles";
import { type CourseDetail, coursesApi } from "../../api/courses";
import ConfirmModal from "../ConfirmModal";
import CourseEditModel from "./CourseEditModel";
import { useNavigate } from "react-router-dom";

const CourseDetailComponent = ( {courseId} : { courseId: string } ) => {
  const navigate = useNavigate();

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const editModalController = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await coursesApi.delete(courseId);
      navigate('/geral/cursos');
    } catch (error) {
      console.error("Erro ao eliminar curso:", error);
    } finally {
      setDeleting(false);
      setIsDeleteModalOpen(false);
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
        <button
          onClick={() => {
            editModalController[1](true)
          }}
          className={`flex-1 px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors`}
        >
          Editar
        </button>

        <button
          onClick={() => setIsDeleteModalOpen(true)}
          className={`flex-1 px-6 py-3 ${btn.danger} rounded-md font-medium transition-colors`}
        >
          Eliminar
        </button>
      </div>

      <CourseEditModel
        controller={editModalController}
        onSave={(courseData) => setCourse(courseData)}
        courseData={course}
      />

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        title="Eliminar curso"
        message={`Tem certeza que deseja eliminar "${course.name}"?`}
        confirmLabel="Eliminar"
        variant="danger"
        loading={deleting}
        onCancel={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
      />
    </div>
  );
};

export default CourseDetailComponent;
