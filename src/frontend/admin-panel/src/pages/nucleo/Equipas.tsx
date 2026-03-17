import { useState, useEffect } from 'react';
import HelpTooltip from '../../components/HelpTooltip';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { teamsApi } from '../../api/teams';
import type { Team } from '../../api/teams';
import { modalitiesApi } from '../../api/modalities';
import type { Modality } from '../../api/modalities';
import { coursesApi } from '../../api/courses';
import type { Course } from '../../api/courses';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';

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
  const { notify } = useNotification();
  const [filterModality, setFilterModality] = useState('');
  const [filterCourse, setFilterCourse] = useState('');

  // Get only modalities and courses that have teams (for filtering)
  const availableModalities = allModalities.filter(modality =>
    teams.some(team => team.modality.id === modality.id)
  );

  const availableCourses = allCourses.filter(course =>
    teams.some(team => team.course.id === course.id)
  );

  // Fetch teams, modalities, and courses from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

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
        notify('Não foi possível carregar os dados das equipas e modalidades. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Default team name when creating team
  useEffect(() => {
    if (selectedCourse) {
      const course = allCourses.find(c => String(c.id) === String(selectedCourse));
      if (course) {
        setNewTeamName(course.name);
      }
    }
  }, [selectedCourse, allCourses]);

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
      setTeams([...teams, newTeam]);
      setNewTeamName('');
      setSelectedModality('');
      setSelectedCourse('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create team:', err);
      notify('Não foi possível criar a equipa. Verifique os dados e tente novamente.', 'error');
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
    const matchesModality = filterModality ? team.modality.id === filterModality : true;
    const matchesCourse = filterCourse ? team.course.id === filterCourse : true;
    return matchesModality && matchesCourse;
  });

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Equipas</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2`}
            >
              <span>+</span>
              Adicionar Equipa
            </button>
          </div>

          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {!loading && (
            <>
              <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
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

              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Equipas</h2>
                <div className="space-y-3">
                  {filteredTeams.length > 0 ? (
                    filteredTeams.map((team) => (
                      <button
                        key={team.id}
                        type="button"
                        onClick={() => navigate(`/nucleo/equipas/${team.id}`)}
                        className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                      >
                        <div className="flex justify-between items-center">
                          <span className="text-gray-800 font-medium">{team.name}</span>
                          <div className="flex gap-4 text-sm">
                            <span className="text-teal-600 font-medium">{getModalityName(team.modality.id)}</span>
                            <span className="text-gray-500">{getCourseName(team.course.id)}</span>
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
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Equipa</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="course" className="block text-gray-700 font-medium mb-2">
                  Curso <HelpTooltip text="Curso académico que esta equipa representa. Afeta os filtros de pesquisa e a organização das equipas." className="ml-1" /> <span className="text-red-500">*</span>
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
              <div>
                <label htmlFor="teamName" className="block text-gray-700 font-medium mb-2">
                  Nome da Equipa <HelpTooltip text="Nome pelo qual a equipa é identificada nos torneios e rankings. Deve ser único dentro do núcleo." className="ml-1" /> <span className="text-red-500">*</span>
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
                <label htmlFor="modality" className="block text-gray-700 font-medium mb-2">
                  Modalidade <HelpTooltip text="Desporto para o qual esta equipa está inscrita. A equipa só pode participar em torneios da mesma modalidade." className="ml-1" /> <span className="text-red-500">*</span>
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


            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewTeamName('');
                  setSelectedModality('');
                  setSelectedCourse('');
                }}
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
      )}
    </div>
  );
};

export default Equipas;
