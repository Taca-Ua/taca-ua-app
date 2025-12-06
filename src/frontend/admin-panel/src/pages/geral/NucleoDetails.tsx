import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { coursesApi, type Course } from '../../api/courses';

const NucleoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [nucleus, setNucleus] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [editedLogoUrl, setEditedLogoUrl] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await coursesApi.getById(Number(id));
        setNucleus(data);
        setError('');
      } catch (err) {
        console.error('Failed to fetch course:', err);
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
    setEditedDescription(nucleus.description || '');
    setEditedLogoUrl(nucleus.logo_url || '');
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
      const updatedNucleus = await coursesApi.update(Number(id), {
        abbreviation: editedAbbreviation,
        name: editedName,
        description: editedDescription || undefined,
        logo_url: editedLogoUrl || undefined,
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
        await coursesApi.delete(Number(id));
        navigate('/geral/nucleos');
      } catch (err) {
        console.error('Failed to delete course:', err);
        setError('Erro ao eliminar núcleo');
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

  if (!nucleus) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Núcleo</h1>
            <button
              onClick={() => navigate('/geral/nucleos')}
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
                  {nucleus.logo_url ? (
                    <img src={nucleus.logo_url} alt={nucleus.abbreviation} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-teal-600 font-bold text-2xl">{nucleus.abbreviation}</span>
                  )}
                </div>
                {nucleus.logo_url && (
                  <span className="text-gray-600 text-sm">{nucleus.logo_url}</span>
                )}
              </div>
            </div>

            {/* Abbreviation */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Abreviatura</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {nucleus.abbreviation}
              </div>
            </div>

            {/* Nome */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {nucleus.name}
              </div>
            </div>

            {/* Description */}
            {nucleus.description && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Descrição</label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {nucleus.description}
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

      {/* MODAL Edition */}
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

              {/* NAME */}
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

              {/* Description */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Descrição</label>
                <textarea
                  value={editedDescription}
                  onChange={(e) => setEditedDescription(e.target.value)}
                  placeholder="Digite a descrição"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[80px]"
                />
              </div>

              {/* Logo URL */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Logo URL</label>
                <input
                  type="url"
                  value={editedLogoUrl}
                  onChange={(e) => setEditedLogoUrl(e.target.value)}
                  placeholder="https://exemplo.com/logo.png"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                {editedLogoUrl && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-gray-600 text-sm">Preview:</span>
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
                      <img src={editedLogoUrl} alt="Preview" className="w-full h-full object-cover" onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }} />
                    </div>
                  </div>
                )}
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
