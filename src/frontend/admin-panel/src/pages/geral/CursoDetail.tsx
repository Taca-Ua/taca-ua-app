import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { coursesApi, type Course } from '../../api/courses';
import { nucleosApi, type Nucleo } from '../../api/nucleos';

const CursoDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [course, setCourse] = useState<Course>();
  const [nucleos, setNucleos] = useState<Nucleo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [editedNucleoId, setEditedNucleoId] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await coursesApi.getById(String(id));
        setCourse(data);
        setError('');
      } catch (err) {
        console.error('Failed to fetch course:', err);
        setError('Erro ao carregar curso');
        navigate('/geral/cursos');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate]);

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

  const handleEdit = () => {
    if (!course) return;
    setEditedName(course.name);
    setEditedAbbreviation(course.abbreviation);
    setEditedDescription(course.description || '');
    setEditedNucleoId(getNucleoIdFromName(course.nucleo));
    setError('');
    setIsEditModalOpen(true);
  };

  const getNucleoIdFromName = (nucleoName: string): string => {
	const nucleo = nucleos.find((n) => n.name === nucleoName);
	return nucleo ? nucleo.id : '';
  };

  const handleSave = async () => {
    if (!editedName.trim()) {
      setError('Nome é obrigatório');
      return;
    }
    if (!editedAbbreviation.trim()) {
      setError('Abreviatura é obrigatória');
      return;
    }
    if (!editedNucleoId) {
      setError('Núcleo é obrigatório');
      return;
    }

    try {
      const updatedCourse = await coursesApi.update(String(id), {
        name: editedName,
        abbreviation: editedAbbreviation,
        description: editedDescription.trim() || undefined,
        nucleo_id: editedNucleoId,
      });
      setCourse(updatedCourse);
      setError('');
      setIsEditModalOpen(false);
    } catch (err) {
      console.error('Failed to update course:', err);
      setError('Erro ao atualizar curso');
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Tem certeza que deseja eliminar "${course?.name}"?`)) {
      try {
        await coursesApi.delete(String(id));
        navigate('/geral/cursos');
      } catch (err) {
        console.error('Failed to delete course:', err);
        setError('Erro ao eliminar curso');
      }
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

  if (!course) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Curso</h1>
            <button
              onClick={() => navigate('/geral/cursos')}
              className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
            >
              Voltar
            </button>
          </div>

          {/* Card */}
          <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
            {/* Logo */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Logo</label>
              <div className="flex items-center gap-4">
                <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
                  {course.logo_url ? (
                    <img
                      src={course.logo_url}
                      alt={course.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        e.currentTarget.parentElement!.innerHTML = `<span class="text-teal-600 font-bold text-2xl">${course.abbreviation}</span>`;
                      }}
                    />
                  ) : (
                    <span className="text-teal-600 font-bold text-2xl">{course.abbreviation}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Name */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {course.name}
              </div>
            </div>

            {/* Abbreviation */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Abreviatura</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {course.abbreviation}
              </div>
            </div>

            {/* Description */}
            {course.description && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Descrição</label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {course.description}
                </div>
              </div>
            )}

            {/* Nucleo */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Núcleo</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {course.nucleo ? course.nucleo : 'N/A'}
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <button
                onClick={handleEdit}
                className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              >
                Editar
              </button>

              <button
                onClick={handleDelete}
                className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* MODAL Edition */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Curso</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  placeholder="Digite o nome do curso"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              {/* Abbreviation */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Abreviatura <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={editedAbbreviation}
                  onChange={(e) => setEditedAbbreviation(e.target.value)}
                  placeholder="Ex: MECT, LEI, LECI"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Descrição</label>
                <textarea
                  value={editedDescription}
                  onChange={(e) => setEditedDescription(e.target.value)}
                  placeholder="Digite a descrição (opcional)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[80px]"
                />
              </div>

              {/* Nucleo */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Núcleo <span className="text-red-500">*</span>
                </label>
                <select
                  value={editedNucleoId}
                  onChange={(e) => setEditedNucleoId(e.target.value)}
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
                  setIsEditModalOpen(false);
                  setError('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md"
              >
                Cancelar
              </button>

              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CursoDetail;
