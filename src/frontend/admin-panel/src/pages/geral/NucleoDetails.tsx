import { useState, useEffect } from 'react';
import HelpTooltip from '../../components/HelpTooltip';
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

  // Estados para Edição
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');
  const [editedLogoFile, setEditedLogoFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

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
        notify('Não foi possível carregar os dados do núcleo.', 'error');
        navigate('/geral/nucleos');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate, notify]);

  const handleEdit = () => {
    if (!nucleus) return;
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
    setPreviewUrl(nucleus.logo_url || null);
    setEditedLogoFile(null);
    setIsEditModalOpen(true);
  };

  const handleSave = async () => {
    if (!editedAbbreviation.trim() || !editedName.trim()) {
      notify('Campos obrigatórios em falta.', 'error');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('name', editedName.trim());
      formData.append('abbreviation', editedAbbreviation.trim());
      
      if (editedLogoFile) {
        formData.append('logo', editedLogoFile);
      }

      const updatedNucleus = await nucleosApi.update(String(id), formData);
      setNucleus(updatedNucleus);
      setIsEditModalOpen(false);
      notify('Núcleo atualizado com sucesso!', 'success');
    } catch (err) {
      console.error('Failed to update nucleus:', err);
      notify('Não foi possível guardar as alterações.', 'error');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setEditedLogoFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleDelete = () => {
    setIsDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    try {
      setDeleting(true);
      await nucleosApi.delete(String(id));
      notify('Núcleo eliminado com sucesso.', 'success');
      navigate('/geral/nucleos');
    } catch (err) {
      console.error('Failed to delete nucleus:', err);
      notify('Não foi possível eliminar o núcleo.', 'error');
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
                <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500 shadow-sm">
                  {nucleus.logo_url ? (
                    <img src={nucleus.logo_url} alt="Logo" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-teal-600 font-bold text-2xl">{nucleus.abbreviation.substring(0, 3).toUpperCase()}</span>
                  )}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-teal-500 font-medium mb-2">Abreviatura <HelpTooltip text="Sigla do núcleo." className="ml-1" /></label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800 font-medium uppercase">
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
                    {[...nucleoCourses].sort((a, b) => a.name.localeCompare(b.name)).map(course => (
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
              <div className="flex flex-col items-center mb-4">
                <div className="w-20 h-20 rounded-full border-2 border-teal-500 overflow-hidden mb-3 bg-gray-50 flex items-center justify-center">
                  {previewUrl ? (
                    <img src={previewUrl} className="w-full h-full object-cover" alt="Preview" />
                  ) : (
                    <span className="text-gray-400 text-xs">Sem Logo</span>
                  )}
                </div>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Abreviatura <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={editedAbbreviation}
                  onChange={(e) => setEditedAbbreviation(e.target.value)}
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsEditModalOpen(false)}
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
        onCancel={() => !deleting && setIsDeleteModalOpen(false)}
        onConfirm={confirmDelete}
      />
    </div>
  );
};

export default NucleoDetails;