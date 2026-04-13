import { useEffect, useState } from "react";
import { teamsApi, type TeamListItem } from "../../api/teams";
import { modalitiesApi, type ModalityListItem } from "../../api/modalities";
import { coursesApi, type CourseListItem } from "../../api/courses";
import HelpTooltip from "../HelpTooltip";
import { btn } from "../../styles/buttonStyles";
import { useNotification } from "../../contexts/NotificationProvider";

const TeamsCreateModel = ({
  controller,
  onCreate,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onCreate?: (newTeam: TeamListItem) => void;
}) => {
  const { notify } = useNotification();
  const [isOpen, setIsOpen] = controller;

  const [newTeamName, setNewTeamName] = useState('');
  const [selectedModality, setSelectedModality] = useState('');
  const [selectedCourse, setSelectedCourse] = useState('');

  const [allModalities, setAllModalities] = useState<ModalityListItem[]>([]);
  const [allCourses, setAllCourses] = useState<CourseListItem[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modalities, courses] = await Promise.all([
          modalitiesApi.getAll(),
          coursesApi.getAll(),
        ]);
        setAllModalities(modalities);
        setAllCourses(courses);
      } catch (err) {
        console.error('Failed to fetch modalities or courses:', err);
        notify('Não foi possível carregar as modalidades ou cursos. Tente recarregar a página.', 'error');
      }
    };

    if (isOpen) {
      fetchData();
    }
  }, [isOpen, notify]);

  const onClose = () => {
    setIsOpen(false);
    setNewTeamName("");
    setSelectedModality("");
    setSelectedCourse("");
  }

  const handleAddTeam = async () => {
    if (!newTeamName.trim()) {
      notify('Por favor, preencha o nome da equipa.', 'error');
      return;
    }

    if (!selectedModality) {
      notify('Por favor, selecione uma modalidade.', 'error');
      return;
    }

    if (!selectedCourse) {
      notify('Por favor, selecione um curso.', 'error');
      return;
    }

    try {
      const newTeam = await teamsApi.create({
        modality_id: selectedModality,
        course_id: selectedCourse,
        name: newTeamName,
      });

      // Add to local state
      if (onCreate) onCreate(newTeam);
      onClose();
    } catch (err) {
      console.error('Failed to create team:', err);
      notify('Não foi possível criar a equipa. Verifique os dados e tente novamente.', 'error');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Equipa
        </h2>

        <div className="space-y-4">
          <div>
            <label
              htmlFor="course"
              className="block text-gray-700 font-medium mb-2"
            >
              Curso{" "}
              <HelpTooltip
                text="Curso académico que esta equipa representa. Afeta os filtros de pesquisa e a organização das equipas."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <select
              id="course"
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Selecionar Curso</option>
              {[...allCourses]
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.name}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label
              htmlFor="teamName"
              className="block text-gray-700 font-medium mb-2"
            >
              Nome da Equipa{" "}
              <HelpTooltip
                text="Nome pelo qual a equipa é identificada nos torneios e rankings. Deve ser único dentro do núcleo."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="teamName"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Digite o nome da equipa"
            />
          </div>

          <div>
            <label
              htmlFor="modality"
              className="block text-gray-700 font-medium mb-2"
            >
              Modalidade{" "}
              <HelpTooltip
                text="Desporto para o qual esta equipa está inscrita. A equipa só pode participar em torneios da mesma modalidade."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <select
              id="modality"
              value={selectedModality}
              onChange={(e) => setSelectedModality(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Selecionar Modalidade</option>
              {[...allModalities]
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((modality) => (
                  <option key={modality.id} value={modality.id}>
                    {modality.name}
                  </option>
                ))}
            </select>
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
            onClick={handleAddTeam}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
          >
            Adicionar
          </button>
        </div>
      </div>
    </div>
  );
};

export default TeamsCreateModel;
