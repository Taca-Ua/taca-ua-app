import { useState } from "react";
import { teamsApi, type TeamListItem } from "../../api/teams";
import { modalitiesApi } from "../../api/modalities";
import { coursesApi } from "../../api/courses";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import ChoseOneInput from "../utils/inputs/ChoseOneInput";
import { useSeason } from "../../contexts/SeasonContext";

const TeamsCreateModal = ({
  onCreate,
}: {
  onCreate?: (newTeam: TeamListItem) => void;
}) => {
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [newTeamName, setNewTeamName] = useState('');
  const [selectedModality, setSelectedModality] = useState('');
  const [selectedCourse, setSelectedCourse] = useState('');
  const { loadedSeason } = useSeason();

  const onClose = () => {
    popModal();
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
        season_id: loadedSeason?.id
      });

      // Add to local state
      if (onCreate) onCreate(newTeam);
      onClose();
      notify('Equipa criada com sucesso!', 'success');
    } catch (err) {
      console.error('Failed to create team:', err);
      notify('Não foi possível criar a equipa. Verifique os dados e tente novamente.', 'error');
    }
  };

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
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
            <ChoseOneInput
              allElementsLoader={() => coursesApi.getAll(
                loadedSeason?.id
              ).then(courses => courses.filter(course => course.belongs_to_season).map(course => ({ id: course.id, title: course.name })))}
              onSelect={(ele) => setSelectedCourse(ele?.id || "")}
            />
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
            <ChoseOneInput
              allElementsLoader={() => modalitiesApi.getAll({
                  season_id: loadedSeason?.id
              }).then(modalities => modalities.filter(modality => modality.belongs_to_season).map(modality => ({ id: modality.id, title: modality.name })))}
              onSelect={(ele) => setSelectedModality(ele?.id || "")}
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
            onClick={handleAddTeam}
            type="primary"
            flexible={true}
          >
            Adicionar
          </Button>
        </div>
      </div>
  );
};

export default TeamsCreateModal;
