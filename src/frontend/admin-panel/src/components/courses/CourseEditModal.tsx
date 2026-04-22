import { useEffect, useState } from "react";
import HelpTooltip from "../HelpTooltip";
import { nucleosApi } from "../../api/nucleos";
import { type CourseDetail, coursesApi } from "../../api/courses";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import ChoseOneInput from "../utils/inputs/ChoseOneInput";

const CourseEditModal = ({
  controller,
  courseState,
  onSave,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  courseState: [CourseDetail, React.Dispatch<React.SetStateAction<CourseDetail | null>>];
  onSave?: (courseData: CourseDetail) => void;
}) => {

  const [isOpen, setIsOpen] = controller;
  const { notify } = useNotification();

  const [courseData, setCourseData] = courseState;
  const [editedName, setEditedName] = useState(courseData.name);
  const [editedAbbreviation, setEditedAbbreviation] = useState(courseData.abbreviation);
  const [editedNucleoId, setEditedNucleoId] = useState(courseData.nucleo.id);

  useEffect(() => {
    if (!isOpen) return;

    setEditedName(courseData.name);
    setEditedAbbreviation(courseData.abbreviation);
    setEditedNucleoId(courseData.nucleo.id);
  }, [courseData, isOpen]);

  const onClose = () => {

    setEditedName(courseData.name);
    setEditedAbbreviation(courseData.abbreviation);
    setEditedNucleoId(courseData.nucleo.id);
    setIsOpen(false);
  }

  const handleSave = () => {
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

    coursesApi.update(courseData.id, {
      name: editedName,
      abbreviation: editedAbbreviation,
      nucleo_id: editedNucleoId,
    }).then(updatedCourse => {
      setCourseData(updatedCourse);
      if (onSave) onSave(updatedCourse);
      setIsOpen(false);
      notify('Curso atualizado com sucesso', 'success');
    }).catch(error => {
      console.error("Error updating course:", error);
      notify('Erro ao atualizar curso', 'error');
    });
  };

  if (!isOpen) return null;

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
            <ChoseOneInput
              allElementsLoader={() => nucleosApi.getAll().then(nucleos => nucleos.map(n => ({ id: n.id, title: n.abbreviation, subTitle: n.name })))}
              onSelect={(elem) => setEditedNucleoId(elem?.id || "")}
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
            Salvar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CourseEditModal;
