import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ConfirmModal from '../../components/ConfirmModal';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { nucleosApi, type Nucleo } from '../../api/nucleos';
import { coursesApi, type Course } from '../../api/courses';
import { btn } from '../../styles/buttonStyles';

const NucleoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [nucleus, setNucleus] = useState<Nucleo>();
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [nucleoCourses, setNucleoCourses] = useState<Course[]>([]);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await nucleosApi.getById(String(id));
        setNucleus(data);
        const allCourses = await coursesApi.getAll();
        setNucleoCourses(allCourses.filter(c => c.nucleo.id === String(id)));
      } catch (err) {
        console.error('Failed to fetch núcleo:', err);
        notify('Não foi possível carregar os dados do núcleo. Tente recarregar a página.', 'error');
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
    setIsEditModalOpen(true);
  };

  const handleSave = async () => {
    if (!editedAbbreviation.trim()) {
      notify('Abreviatura é obrigatória', 'error');
      return;
    }
    if (!editedName.trim()) {
      notify('Nome é obrigatório', 'error');
      return;
    }

    try {
      const updatedNucleus = await nucleosApi.update(String(id), {
        abbreviation: editedAbbreviation,
        name: editedName,
      });
      setNucleus(updatedNucleus);
      setIsEditModalOpen(false);
    } catch (err) {
      console.error('Failed to update course:', err);
      notify('Não foi possível guardar as alterações ao núcleo. Tente novamente.', 'error');
    }
  };

  const handleDelete = () => {
    setIsDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    try {
      setDeleting(true);
      await nucleosApi.delete(String(id));
      navigate('/geral/nucleos');
    } catch (err) {
      console.error('Failed to delete course:', err);
      notify('Não foi possível eliminar o núcleo. Poderá ter cursos ou membros associados.', 'error');
    } finally {
      setDeleting(false);
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
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
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
                className={`flex-1 px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors`}
              >
                Editar
              </button>

              <button
                onClick={handleDelete}
                className={`flex-1 px-6 py-3 ${btn.danger} rounded-md font-medium transition-colors`}
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
                }}
                className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md`}
              >
                Cancelar
              </button>

              <button
                onClick={handleSave}
                className={`flex-1 px-4 py-2 ${btn.primary} rounded-md`}
              >
                Guardar
              </button>
            </div>

          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        title="Eliminar núcleo"
        message={`Tem certeza que deseja eliminar "${nucleus.name}"?`}
        confirmLabel="Eliminar"
        variant="danger"
        loading={deleting}
        onCancel={() => {
          if (!deleting) {
            setIsDeleteModalOpen(false);
          }
        }}
        onConfirm={confirmDelete}
      />
    </div>
  );
};

export default NucleoDetails;
