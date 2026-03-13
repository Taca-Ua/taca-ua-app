import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { coursesApi, type Course } from '../../api/courses';
import { nucleosApi, type Nucleo } from '../../api/nucleos';

const CourseEntry = (course: Course) => {
  const navigate = useNavigate();

  return (
    <div
      key={course.id}
      onClick={() => navigate(`/geral/cursos/${course.id}`)}
      className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
    >
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center border-2 border-teal-500 flex-shrink-0">
          <span className="text-teal-600 font-bold text-xs">{course.abbreviation}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-teal-600 font-bold text-lg">{course.abbreviation}</span>
          <span className="text-gray-400">|</span>
          <span className="text-gray-800 font-medium">{course.name}</span>
        </div>
      </div>
      <span className="text-gray-500 text-sm">{course.nucleo.name}</span>
    </div>
  );
};

const Cursos = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCourseName, setNewCourseName] = useState('');
  const [newCourseAbbreviation, setNewCourseAbbreviation] = useState('');
  const [selectedNucleoId, setSelectedNucleoId] = useState('');

  const [courses, setCourses] = useState<Course[]>([]);
  const [nucleos, setNucleos] = useState<Nucleo[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [searchQuery, setSearchQuery] = useState('');
  const [nucleoFilter, setNucleoFilter] = useState('');

  // Fetch courses on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await coursesApi.getAll();
        setCourses(data);
      } catch (err) {
        console.error('Failed to fetch courses:', err);
        notify('Não foi possível carregar a lista de cursos. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Fetch nucleos on mount
  useEffect(() => {
    const fetchNucleos = async () => {
      try {
        const data = await nucleosApi.getAll();
        setNucleos(data);
      } catch (err) {
        console.error('Failed to fetch nucleos:', err);
      }
    };

    fetchNucleos();
  }, []);

  const handleAddCourse = async () => {
    if (!newCourseName.trim()) {
      notify('Por favor, preencha o nome do curso.', 'error');
      return;
    }

    if (!newCourseAbbreviation.trim()) {
      notify('Por favor, preencha a abreviatura do curso.', 'error');
      return;
    }

    if (!selectedNucleoId) {
      notify('Por favor, selecione um núcleo.', 'error');
      return;
    }

    try {
      const newCourse = await coursesApi.create({
        name: newCourseName,
        abbreviation: newCourseAbbreviation,
        nucleo_id: selectedNucleoId,
      });

      setCourses([...courses, newCourse]);

      // Reset
      setNewCourseName('');
      setNewCourseAbbreviation('');
      setSelectedNucleoId('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create course:', err);
      notify('Não foi possível criar o curso. Verifique os dados e tente novamente.', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Curso
            </button>
          </div>

          <div className="mb-6 flex gap-3">
            <input
              type="text"
              placeholder="Pesquisar curso..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <select
              value={nucleoFilter}
              onChange={(e) => setNucleoFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="">Todos os núcleos</option>
              {[...nucleos].sort((a, b) => a.name.localeCompare(b.name)).map(n => (
                <option key={n.id} value={n.id}>{n.name}</option>
              ))}
            </select>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="space-y-3">
              {courses.length > 0 ? (
                [...courses]
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .filter((c) =>
                    (c.name.toLowerCase().includes(searchQuery.toLowerCase()) || c.abbreviation.toLowerCase().includes(searchQuery.toLowerCase())) &&
                    (nucleoFilter === '' || c.nucleo.id === nucleoFilter)
                  )
                  .map((course) => (
                  <CourseEntry
                    key={course.id}
                    {...course}
                  />
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Nenhum curso encontrado.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Curso</h2>

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
                  Abreviatura <span className="text-red-500">*</span>
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
                  Núcleo <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedNucleoId}
                  onChange={(e) => setSelectedNucleoId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Núcleo</option>
                  {nucleos.map((nucleo) => (
                    <option key={nucleo.id} value={nucleo.id}>
                      {nucleo.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewCourseName('');
                  setNewCourseAbbreviation('');
                  setSelectedNucleoId('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddCourse}
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

export default Cursos;
