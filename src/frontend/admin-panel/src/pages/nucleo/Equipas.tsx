import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { teamsApi } from '../../api/teams';
import type { Team } from '../../api/teams';
import { modalitiesApi } from '../../api/modalities';
import type { Modality } from '../../api/modalities';
import { coursesApi } from '../../api/courses';
import type { Course } from '../../api/courses';

const Equipas = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [selectedModality, setSelectedModality] = useState('');
  const [selectedCourse, setSelectedCourse] = useState('');
  const [teams, setTeams] = useState<Team[]>([]);
  const [allModalities, setAllModalities] = useState<Modality[]>([]);
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterModality, setFilterModality] = useState('');
  const [filterCourse, setFilterCourse] = useState('');

  // Get only modalities and courses that have teams (for filtering)
  const availableModalities = allModalities.filter(modality =>
    teams.some(team => team.modality_name === modality.id)
  );

  const availableCourses = allCourses.filter(course =>
    teams.some(team => team.course_name === course.id)
  );

  // Fetch teams, modalities, and courses from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch teams, modalities, and courses in parallel
        const [fetchedTeams, fetchedModalities, fetchedCourses] = await Promise.all([
          teamsApi.getAll(),
          modalitiesApi.getAll(),
          coursesApi.getAll(),
        ]);

        console.log('Fetched teams:', fetchedTeams);
        console.log('Fetched modalities:', fetchedModalities);
        console.log('Fetched courses:', fetchedCourses);

        setTeams(fetchedTeams);
        setAllModalities(fetchedModalities);
        setAllCourses(fetchedCourses);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Erro ao carregar dados. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddTeam = async () => {
    if (!newTeamName.trim()) {
      alert('Por favor, preencha o nome da equipa.');
      return;
    }

    if (!selectedModality) {
      alert('Por favor, selecione uma modalidade.');
      return;
    }

    if (!selectedCourse) {
      alert('Por favor, selecione um curso.');
      return;
    }

    try {
      const newTeam = await teamsApi.create({
        modality_id: selectedModality,
        course_id: selectedCourse,
        name: newTeamName,
      });

      // Add to local state
      setTeams([...teams, newTeam]);
      setNewTeamName('');
      setSelectedModality('');
      setSelectedCourse('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create team:', err);
      alert('Erro ao criar equipa. Por favor, tente novamente.');
    }
  };

  // Helper function to get modality name from ID
  const getModalityName = (modalityId: string) => {
    const modality = allModalities.find(m => m.id === modalityId);
    return modality ? modality.name : `Modalidade ${modalityId}`;
  };

  // Helper function to get course name from ID
  const getCourseName = (courseId: string) => {
    const course = allCourses.find(c => c.id === courseId);
    return course ? course.name : `Curso ${courseId}`;
  };

  // Filter teams by modality and/or course
  const filteredTeams = teams.filter((team) => {
    const matchesModality = filterModality ? team.modality_name === filterModality : true;
    const matchesCourse = filterCourse ? team.course_name === filterCourse : true;
    return matchesModality && matchesCourse;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Equipas</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Equipa
            </button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}

          {/* Content - Only show when not loading */}
          {!loading && !error && (
            <>
              {/* Filters */}
              <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Modality Filter */}
                <div>
                  <label htmlFor="modalityFilter" className="block text-gray-700 font-medium mb-2">
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

                {/* Course Filter */}
                <div>
                  <label htmlFor="courseFilter" className="block text-gray-700 font-medium mb-2">
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
                    ))}
                  </select>
                </div>
              </div>

              {/* Teams List */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Equipas</h2>
                <div className="space-y-3">
                  {filteredTeams.length > 0 ? (
                    filteredTeams.map((team) => (
                      <div
                        key={team.id}
                        onClick={() => navigate(`/nucleo/equipas/${team.id}`)}
                        className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors"
                      >
                        <div className="flex justify-between items-center">
                          <span className="text-gray-800 font-medium">{team.name}</span>
                          <div className="flex gap-4 text-sm">
                            <span className="text-teal-600 font-medium">{getModalityName(team.modality_name)}</span>
                            <span className="text-gray-500">{getCourseName(team.course_name)}</span>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-8">
                      Nenhuma equipa encontrada com os filtros selecionados.
                    </p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Add Team Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Equipa</h2>

            <div className="space-y-4">
              {/* Team Name */}
              <div>
                <label htmlFor="teamName" className="block text-gray-700 font-medium mb-2">
                  Nome da Equipa <span className="text-red-500">*</span>
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

              {/* Modality Selection */}
              <div>
                <label htmlFor="modality" className="block text-gray-700 font-medium mb-2">
                  Modalidade <span className="text-red-500">*</span>
                </label>
                <select
                  id="modality"
                  value={selectedModality}
                  onChange={(e) => setSelectedModality(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Modalidade</option>
                  {allModalities.map((modality) => (
                    <option key={modality.id} value={modality.id}>
                      {modality.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Course Selection */}
              <div>
                <label htmlFor="course" className="block text-gray-700 font-medium mb-2">
                  Curso <span className="text-red-500">*</span>
                </label>
                <select
                  id="course"
                  value={selectedCourse}
                  onChange={(e) => setSelectedCourse(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Curso</option>
                  {allCourses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewTeamName('');
                  setSelectedModality('');
                  setSelectedCourse('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddTeam}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              >
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Equipas;
