import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { coursesApi, type Course } from '../../api/courses';

const Nucleo = () => {
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newNucleusAbbreviation, setNewNucleusAbbreviation] = useState('');
  const [newNucleusName, setNewNucleusName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newLogoUrl, setNewLogoUrl] = useState('');

  const [nuclei, setNuclei] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');



  // Fetch courses on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await coursesApi.getAll();
        setNuclei(data);
        setError('');
      } catch (err) {
        console.error('Failed to fetch courses:', err);
        setError('Erro ao carregar núcleos');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Agregar nuevo núcleo
  const handleAddNucleus = async () => {
    if (!newNucleusAbbreviation.trim()) {
      setError('Por favor, preencha a abreviatura do núcleo.');
      return;
    }

    if (!newNucleusName.trim()) {
      setError('Por favor, preencha o nome do núcleo.');
      return;
    }

    try {
      const newNucleus = await coursesApi.create({
        abbreviation: newNucleusAbbreviation,
        name: newNucleusName,
        description: newDescription || undefined,
        logo_url: newLogoUrl || undefined,
      });

      setNuclei([...nuclei, newNucleus]);
      setError('');

      // Reset
      setNewNucleusAbbreviation('');
      setNewNucleusName('');
      setNewDescription('');
      setNewLogoUrl('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create course:', err);
      setError('Erro ao criar núcleo');
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
            <h1 className="text-3xl font-bold text-gray-800">Núcleos</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Núcleo
            </button>
          </div>

          {/* Nuclei List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Núcleos</h2>

            <div className="space-y-3">
              {nuclei.length > 0 ? (
                nuclei.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => navigate(`/geral/nucleos/${n.id}`)}
                    className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
                  >
                    <div className="flex items-center gap-4">
                      {/* Logo */}
                      <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500 flex-shrink-0">
                        {n.logo_url ? (
                          <img src={n.logo_url} alt={n.abbreviation} className="w-full h-full object-cover" />
                        ) : (
                          <span className="text-teal-600 font-bold text-sm">{n.abbreviation}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-teal-600 font-bold text-lg">{n.abbreviation}</span>
                        <span className="text-gray-400">|</span>
                        <span className="text-gray-800 font-medium">{n.name}</span>
                      </div>
                    </div>
                    {n.description && (
                      <span className="text-gray-600 text-sm">{n.description}</span>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Nenhum núcleo encontrado.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Nucleus Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Núcleo</h2>

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
                  value={newNucleusAbbreviation}
                  onChange={(e) => setNewNucleusAbbreviation(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Ex: MECT, LEI, LECI"
                />
              </div>

              {/* Name */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Nome do Núcleo <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newNucleusName}
                  onChange={(e) => setNewNucleusName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome completo"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Descrição
                </label>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[80px]"
                  placeholder="Digite a descrição do núcleo"
                />
              </div>

              {/* Logo URL */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Logo URL
                </label>
                <input
                  type="url"
                  value={newLogoUrl}
                  onChange={(e) => setNewLogoUrl(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="https://exemplo.com/logo.png"
                />
                {newLogoUrl && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-sm text-gray-600">Preview:</span>
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500">
                      <img
                        src={newLogoUrl}
                        alt="Preview"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewNucleusAbbreviation('');
                  setNewNucleusName('');
                  setNewDescription('');
                  setNewLogoUrl('');
                  setError('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddNucleus}
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

export default Nucleo;
