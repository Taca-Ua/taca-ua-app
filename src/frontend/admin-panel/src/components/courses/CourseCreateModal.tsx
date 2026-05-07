import { useState } from "react";
import { coursesApi, type CourseListItem } from "../../api/courses";
import { nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import ChoseOneModal from "../utils/costum_menus/ChoseOneModal";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";
import { useSeason } from "../../contexts/SeasonContext";

const CourseCreateModal = ({
  onCreate,
}: {
  onCreate?: (course: CourseListItem) => void;
}) => {
  const { popModal, pushModal } = useModal();
  const { isAdminGeneral } = useAuth();
  const { loadedSeasonIsTheCurrentSeason, activeSeason } = useSeason();

  const [newCourseName, setNewCourseName] = useState("");
  const [newCourseAbbreviation, setNewCourseAbbreviation] = useState("");
  const [selectedNucleo, setSelectedNucleo] = useState<{id: string, title: string, subTitle?: string} | null>(null);

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
    popModal();
  };

  if (!isAdminGeneral) return null;  // extra layer of security, button to open this modal is also hidden for non-general admins

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Curso
        </h2>

        {!loadedSeasonIsTheCurrentSeason && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-6" role="alert">
            <p className="font-medium">Atenção:</p>
            <p>Este curso será adicionado à temporada ativa: <strong>{activeSeason?.name}</strong></p>
          </div>
        )}

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
              onClick={() => pushModal(
                <ChoseOneModal
                  allElementsLoader={() => nucleosApi.getAll().then(data => data.map((nucleo) => ({
                    id: nucleo.id,
                    title: nucleo.abbreviation,
                    subTitle: nucleo.name,
                  })))}
                  onSelect={(nucleo) => setSelectedNucleo(nucleo)}
                  title="Selecionar Núcleo"
                />
              )}
              className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700 cursor-pointer"
            >
              {selectedNucleo
                ? selectedNucleo.title
                : "Selecionar Núcleo"}
            </div>
          </div>
        </div>

        <div className="flex gap-4 mt-8">
          <Button
            onClick={onClose}
            type="secondary"
            flexible={true}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleAddCourse}
            type="primary"
            flexible={true}
          >
            Adicionar
          </Button>
        </div>
      </div>
  );
}

export default CourseCreateModal
