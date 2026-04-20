import { useEffect, useState } from "react";
import HelpTooltip from "../HelpTooltip";
import { type NucleoListItem, nucleosApi } from "../../api/nucleos";
import { type CourseDetail, coursesApi } from "../../api/courses";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";

const CourseEditModel = ({
  controller,
  onSave,
  courseData,
  courseId,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onSave: (courseData: CourseDetail) => void;
  courseData: CourseDetail;
  courseId?: string;
}) => {
  if (!courseId && !courseData) {
    throw new Error("CourseEditModel requires either courseId or courseData");
  }

  courseId = courseId || courseData.id; // Garantir que temos um courseId para buscar os detalhes, mesmo que courseData seja fornecido

  const { notify } = useNotification();

  const [isOpen, setIsOpen] = controller;

  const [editedName, setEditedName] = useState("");
  const [editedAbbreviation, setEditedAbbreviation] = useState("");
  const [editedNucleoId, setEditedNucleoId] = useState("");
  const [nucleos, setNucleos] = useState<NucleoListItem[]>([]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const fetchNucleos = async () => {
      try {
        const data = await nucleosApi.getAll();
        setNucleos(data);
      } catch (error) {
        console.error("Error fetching nucleos:", error);
      }
    };

    fetchNucleos();
  }, [isOpen]);

  useEffect(() => {
    if (courseData) {
      setEditedName(courseData.name);
      setEditedAbbreviation(courseData.abbreviation);
      setEditedNucleoId(courseData.nucleo.id);
      return;
    }

    const fetchCourse = async () => {
      try {
        const data = await coursesApi.getById(courseId);
        setEditedName(data.name);
        setEditedAbbreviation(data.abbreviation);
        setEditedNucleoId(data.nucleo.id);
      } catch (error) {
        console.error("Error fetching course details:", error);
      }
    };

    fetchCourse();
  }, [courseData, courseId]);

  const onClose = () => {
    setEditedName(courseData.name);
    setEditedAbbreviation(courseData.abbreviation);
    setEditedNucleoId(courseData.nucleo.id);
    setIsOpen(false);
  }

  const handleSave = async () => {
    if (!editedName.trim()) {
      notify('Nome é obrigatório', 'error');
      return;
    }
    if (!editedAbbreviation.trim()) {
      notify('Abreviatura é obrigatória', 'error');
      return;
    }
    if (!editedNucleoId) {
      notify('Núcleo é obrigatório', 'error');
      return;
    }

    try {
      const updatedCourse = await coursesApi.update(courseId, {
        name: editedName,
        abbreviation: editedAbbreviation,
        nucleo_id: editedNucleoId,
      });
      onSave(updatedCourse);
      setIsOpen(false);
      notify('Curso atualizado com sucesso', 'success');
    } catch (error) {
      console.error("Error updating course:", error);
      notify('Erro ao atualizar curso', 'error');
    } finally {
      onClose();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Curso</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              placeholder="Digite o nome do curso"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Abreviatura{" "}
              <HelpTooltip
                text="Código curto do curso, ex: MECT, LEI, LECI. Utilizado como identificador visual no sistema."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={editedAbbreviation}
              onChange={(e) => setEditedAbbreviation(e.target.value)}
              placeholder="Ex: MECT, LEI, LECI"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Núcleo{" "}
              <HelpTooltip
                text="Associação académica (núcleo) a que este curso pertence. Determina qual administrador de núcleo pode gerir este curso."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <select
              value={editedNucleoId}
              onChange={(e) => setEditedNucleoId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Selecionar Núcleo</option>
              {[...nucleos]
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((nucleo) => (
                  <option key={nucleo.id} value={nucleo.id}>
                    {nucleo.name}
                  </option>
                ))}
            </select>
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
            Salvar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CourseEditModel;
