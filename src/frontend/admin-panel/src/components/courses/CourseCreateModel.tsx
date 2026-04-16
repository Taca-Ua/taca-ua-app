import { useState } from "react";
import { coursesApi, type CourseListItem } from "../../api/courses";
import { nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import { btn } from "../../styles/buttonStyles";
import ChoseOneModal from "../utils/costum_menus/ChoseOneModal";

const CourseCreateModel = ({
  controller,
  onCreate,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onCreate?: (course: CourseListItem) => void;
}) => {
  const [isOpen, setIsOpen] = controller;

  const [newCourseName, setNewCourseName] = useState("");
  const [newCourseAbbreviation, setNewCourseAbbreviation] = useState("");
  const [selectedNucleo, setSelectedNucleo] = useState<{id: string, title: string, subTitle?: string} | null>(null);

  const [nucleosSelectModalOpen, setNucleosSelectModalOpen] = useState(false);

  const handleAddCourse = async () => {
    if (!newCourseName.trim()) {
      alert("Por favor, preencha o nome do curso.");
      return;
    }
    if (!newCourseAbbreviation.trim()) {
      alert("Por favor, preencha a abreviatura do curso.");
      return;
    }
    if (!selectedNucleo) {
      alert("Por favor, selecione um núcleo.");
      return;
    }

    try {
      const newCourse = await coursesApi.create({
        name: newCourseName,
        abbreviation: newCourseAbbreviation,
        nucleo_id: selectedNucleo.id,
      });
      if (onCreate) onCreate(newCourse);

      onClose();
    } catch (err) {
      console.error("Failed to create course:", err);
      alert("Não foi possível criar o curso. Tente novamente.");
    }
  };

  const onClose = () => {
    setNewCourseName("");
    setNewCourseAbbreviation("");
    setSelectedNucleo(null);
    setIsOpen(false);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Curso
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome do Curso <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={newCourseName}
              onChange={(e) => setNewCourseName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Digite o nome"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Abreviatura{" "}
              <HelpTooltip
                text="Código curto do curso, ex: MECT, LEI, LECI. Utilizado como identificador visual no sistema e nos perfis de equipa."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={newCourseAbbreviation}
              onChange={(e) => setNewCourseAbbreviation(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Digite a abreviatura"
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
            <div
              onClick={() => setNucleosSelectModalOpen(true)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-pointer"
            >
              {selectedNucleo
                ? selectedNucleo.title
                : "Selecionar Núcleo"}
            </div>
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
            onClick={handleAddCourse}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
          >
            Adicionar
          </button>
        </div>
      </div>

      {/* Nucleo Selection */}
      <ChoseOneModal
        controller={[nucleosSelectModalOpen, setNucleosSelectModalOpen]}
        allElementsLoader={() => nucleosApi.getAll().then(data => data.map((nucleo) => ({
          id: nucleo.id,
          title: nucleo.abbreviation,
          subTitle: nucleo.name,
        })))}
        onSelect={(nucleo) => setSelectedNucleo(nucleo)}
        title="Selecionar Núcleo"
      />
    </div>
  );
}

export default CourseCreateModel
