import { useEffect, useState } from "react";
import { teamsApi, type TeamListItem } from "../../api/teams";
import { useNavigate } from "react-router-dom";

const TeamsListComponent = ({
  teamsState,
}: {
  teamsState?: [
    TeamListItem[],
    React.Dispatch<React.SetStateAction<TeamListItem[]>>,
  ];
}) => {
  const navigate = useNavigate();

  const [teams, setTeams] = teamsState? teamsState : useState<TeamListItem[]>([]);
  const [loading, setLoading] = useState(false);

  const [filterModality, setFilterModality] = useState("");
  const [filterCourse, setFilterCourse] = useState("");

  useEffect(() => {
    const fetchTeams = async () => {
      setLoading(true);
      try {
        const response = await teamsApi.getAll();
        setTeams(response);
      } catch (error) {
        console.error("Erro ao buscar as equipas:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  const availableModalities = teams
    .map((team) => team.modality)
    .filter(
      (modality, index, self) =>
        index === self.findIndex((m) => m.id === modality.id),
    );

  const availableCourses = teams
    .map((team) => team.course)
    .filter(
      (course, index, self) =>
        index === self.findIndex((c) => c.id === course.id),
    );

  const filteredTeams = teams.filter((team) => {
    const matchesModality =
      filterModality === "" || team.modality.id === filterModality;
    const matchesCourse =
      filterCourse === "" || team.course.id === filterCourse;
    return matchesModality && matchesCourse;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
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
          </div>

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
          </div>
        </div>

        <div className="space-y-3">
          {filteredTeams.length > 0 ? (
            filteredTeams.map((team) => (
              <button
                key={team.id}
                type="button"
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
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">
              Nenhuma equipa encontrada com os filtros selecionados.
            </p>
          )}
        </div>
      </div>
    </>
  );
};

export default TeamsListComponent;
