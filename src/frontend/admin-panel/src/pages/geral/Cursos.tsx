import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { coursesApi, type Course } from '../../api/courses';
import { nucleosApi, type Nucleo } from '../../api/nucleos';

const CourseEntry = (course: Course) => {
  const navigate = useNavigate();

  console.log('Rendering CourseEntry for:', course);
  return (
    <div
      key={course.id}
      onClick={() => navigate(`/geral/cursos/${course.id}`)}
      className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
    >
      <div className="flex flex-col">
        <span className="text-gray-800 font-medium">{course.name}</span>
        <span className="text-gray-600 text-sm">
          Abreviatura: {course.abbreviation}
        </span>
      </div>
      <span className="text-gray-600 text-sm">
        Núcleo: {course.nucleo || 'N/A'}
      </span>
    </div>
  );
};

const Cursos = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCourseName, setNewCourseName] = useState('');
  const [newCourseAbbreviation, setNewCourseAbbreviation] = useState('');
  const [newCourseDescription, setNewCourseDescription] = useState('');
  const [selectedNucleoId, setSelectedNucleoId] = useState('');

  const [courses, setCourses] = useState<Course[]>([]);
  const [nucleos, setNucleos] = useState<Nucleo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch courses on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await coursesApi.getAll();
        setCourses(data);
        setError('');
      } catch (err) {
        console.error('Failed to fetch courses:', err);
        setError('Erro ao carregar cursos');
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
      setError('Por favor, preencha o nome do curso.');
      return;
    }

    if (!newCourseAbbreviation.trim()) {
      setError('Por favor, preencha a abreviatura do curso.');
      return;
    }

    if (!selectedNucleoId) {
      setError('Por favor, selecione um núcleo.');
      return;
    }

    try {
      const newCourse = await coursesApi.create({
        name: newCourseName,
        abbreviation: newCourseAbbreviation,
        description: newCourseDescription.trim() || undefined,
        nucleo_id: selectedNucleoId,
      });

      setCourses([...courses, newCourse]);
      setError('');

      // Reset
      setNewCourseName('');
      setNewCourseAbbreviation('');
      setNewCourseDescription('');
      setSelectedNucleoId('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create course:', err);
      setError('Erro ao criar curso');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Curso
            </button>
          </div>

          {/* Courses List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="space-y-3">
              {courses.length > 0 ? (
                courses.map((course) => (
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

      {/* Add Course Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Curso</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
              {/* Name */}
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

              {/* Abbreviation */}
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

              {/* Description */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Descrição
                </label>
                <textarea
                  value={newCourseDescription}
                  onChange={(e) => setNewCourseDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[80px]"
                  placeholder="Digite a descrição (opcional)"
                />
              </div>

              {/* Nucleo */}
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

            {/* Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewCourseName('');
                  setNewCourseAbbreviation('');
                  setNewCourseDescription('');
                  setSelectedNucleoId('');
                  setError('');
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
