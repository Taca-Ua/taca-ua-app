import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { nucleosApi, type Nucleo } from '../../api/nucleos';
import { coursesApi, type Course } from '../../api/courses';

const NucleoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [nucleus, setNucleus] = useState<Nucleo>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [nucleoCourses, setNucleoCourses] = useState<Course[]>([]);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await nucleosApi.getById(String(id));
        setNucleus(data);
        const allCourses = await coursesApi.getAll();
        setNucleoCourses(allCourses.filter(c => c.nucleo.id === String(id)));
        setError('');
      } catch (err) {
        console.error('Failed to fetch núcleo:', err);
        setError('Erro ao carregar núcleo');
        navigate('/geral/nucleos');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate]);

  const handleEdit = () => {
    if (!nucleus) return;
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
    setError('');
    setIsEditModalOpen(true);
  };

  const handleSave = async () => {
    if (!editedAbbreviation.trim()) {
      setError('Abreviatura é obrigatória');
      return;
    }
    if (!editedName.trim()) {
      setError('Nome é obrigatório');
      return;
    }

    try {
      const updatedNucleus = await nucleosApi.update(String(id), {
        abbreviation: editedAbbreviation,
        name: editedName,
      });
      setNucleus(updatedNucleus);
      setError('');
      setIsEditModalOpen(false);
    } catch (err) {
      console.error('Failed to update course:', err);
      setError('Erro ao atualizar núcleo');
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Tem certeza que deseja eliminar "${nucleus?.name}"?`)) {
      try {
        await nucleosApi.delete(String(id));
        navigate('/geral/nucleos');
      } catch (err) {
        console.error('Failed to delete course:', err);
        setError('Erro ao eliminar núcleo');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!nucleus) return null;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Núcleo</h1>
            <button
              onClick={() => navigate('/geral/nucleos')}
              className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
            >
              Voltar
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 space-y-6">

            <div>
              <label className="block text-teal-500 font-medium mb-2">Logo</label>
              <div className="flex items-center gap-4">
                <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
					<span className="text-teal-600 font-bold text-2xl">{nucleus.abbreviation}</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-teal-500 font-medium mb-2">Abreviatura</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {nucleus.abbreviation}
              </div>
            </div>

            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {nucleus.name}
              </div>
            </div>

            {nucleoCourses.length > 0 && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Cursos Associados</label>
                <div className="bg-gray-100 px-4 py-3 rounded-md">
                  <div className="flex flex-wrap gap-2">
                    {nucleoCourses.map(course => (
                      <span
                        key={course.id}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 font-medium"
                      >
                        {course.name}
                        <span className="ml-1 text-blue-600">({course.abbreviation})</span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

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

      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">

            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Núcleo</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
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

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  placeholder="Digite o nome completo"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
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

export default NucleoDetails;
