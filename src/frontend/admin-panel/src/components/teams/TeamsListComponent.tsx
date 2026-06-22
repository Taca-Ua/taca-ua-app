import { useEffect, useState } from "react";
import { type TeamListItem, teamsApi } from "../../api/teams";
import { useNavigate } from "react-router-dom";
import { useSeason } from "../../contexts/SeasonContext";

const TeamsListElement = ({ team }: { team: TeamListItem }) => {
  const navigate = useNavigate();
  return (
    <button
      key={team.id}
      onClick={() => navigate(`/equipas/${team.id}`)}
      className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
    >
      <div className="flex justify-between items-center">
        <span className="text-gray-800 font-medium">{team.name}</span>
        <div className="flex gap-4 text-sm">
          <span className="text-teal-600 font-medium">
            {team.modality.name}
          </span>
          <span className="text-gray-500">{team.course.name}</span>
        </div>
      </div>
    </button>
  );
};

const TeamsListComponent = ({
  teamsState,
  modalityId,
  nucleusId,
  courseId
}: {
  teamsState?: [TeamListItem[] | null, React.Dispatch<React.SetStateAction<TeamListItem[] | null>>];
  modalityId?: string;
  nucleusId?: string;
  courseId?: string;
}) => {
  const { loadedSeason } = useSeason();

  const [teams, setTeams] = teamsState || useState<TeamListItem[] | null>(null);
  const [loading, setLoading] = useState(false);

  const [filterModality, setFilterModality] = useState("");
  const [filterCourse, setFilterCourse] = useState("");

  useEffect(() => {
    if (teams !== null && teams.length > 0) return;

    setLoading(true);
    teamsApi.getAll({
      season_id: loadedSeason?.id,
      modality_id: modalityId,
      nucleus_id: nucleusId,
      course_id: courseId
    })
      .then((data) => {
        setTeams(data);
      })
      .catch((error) => {
        console.error("Erro ao carregar equipas:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [loadedSeason?.id, modalityId, nucleusId]);

  const availableModalities = (teams?.length ? teams : [])
    .map((team) => team.modality)
    .filter(
      (modality, index, self) =>
        index === self.findIndex((m) => m.id === modality.id),
  );

  const availableCourses = (teams?.length ? teams : [])
    .map((team) => team.course)
    .filter(
      (course, index, self) =>
        index === self.findIndex((c) => c.id === course.id),
    );

  const filteredTeams = (teams?.length ? teams : []).filter((team) => {
    const matchesModality =
      filterModality === "" || team.modality.id === filterModality;
    const matchesCourse =
      filterCourse === "" || team.course.id === filterCourse;
    return matchesModality && matchesCourse;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <svg
          className="animate-spin h-8 w-8 text-teal-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"        >
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
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          ></path>
        </svg>
      </div>
    );
  }

  if (!teams || teams.length === 0) {
    return (
      <p className="text-gray-500 text-center py-8">
        Nenhuma equipa encontrada.
      </p>
    );
  }

  return (
      <>
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          {!modalityId && (
            <div>
              <label
                htmlFor="modalityFilter"
                className="block text-gray-700 font-medium mb-2"
              >
                Modalidade
            </label>
            <select
              id="modalityFilter"
              value={filterModality}
              onChange={(e) => setFilterModality(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Todas as Modalidades</option>
              {availableModalities.map((modality) => (
                <option key={modality.id} value={modality.id}>
                  {modality.name}
                </option>
              ))}
            </select>
          </div>)}

          {!courseId && (
            <div>
              <label
                htmlFor="courseFilter"
                className="block text-gray-700 font-medium mb-2"
              >
                Curso
            </label>
            <select
              id="courseFilter"
              value={filterCourse}
              onChange={(e) => setFilterCourse(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Todos os Cursos</option>
              {availableCourses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name}
                </option>
              )).sort((a, b) => a.props.children.localeCompare(b.props.children))}
            </select>
          </div>)}
        </div>

        <div className="space-y-3">
          {filteredTeams.length > 0 ? (
            filteredTeams.map((team) => (
              <TeamsListElement key={team.id} team={team} />
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">
              Nenhuma equipa encontrada com os filtros selecionados.
            </p>
          )}
        </div>
      </>
  );
};

export default TeamsListComponent;
