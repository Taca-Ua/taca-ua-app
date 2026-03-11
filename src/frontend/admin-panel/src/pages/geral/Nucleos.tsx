import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { nucleosApi, type Nucleo as NucleoData } from '../../api/nucleos';

const Nucleo = () => {
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newNucleusAbbreviation, setNewNucleusAbbreviation] = useState('');
  const [newNucleusName, setNewNucleusName] = useState('');

  const [nuclei, setNuclei] = useState<NucleoData[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [searchQuery, setSearchQuery] = useState('');



  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await nucleosApi.getAll();
        setNuclei(data);
      } catch (err) {
        console.error('Failed to fetch courses:', err);
        notify('Não foi possível carregar os núcleos. Verifique a ligação e tente novamente.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddNucleus = async () => {
    if (!newNucleusAbbreviation.trim()) {
      notify('Por favor, preencha a abreviatura do núcleo.', 'error');
      return;
    }

    if (!newNucleusName.trim()) {
      notify('Por favor, preencha o nome do núcleo.', 'error');
      return;
    }

    try {
      const newNucleus = await nucleosApi.create({
		name: newNucleusName,
        abbreviation: newNucleusAbbreviation,
      });

      setNuclei([...nuclei, newNucleus]);
      setNewNucleusAbbreviation('');
      setNewNucleusName('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create course:', err);
      notify('Não foi possível criar o núcleo. Verifique os dados introduzidos e tente novamente.', 'error');
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

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Núcleos</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Núcleo
            </button>
          </div>

          <div className="mb-6">
            <input
              type="text"
              placeholder="Pesquisar núcleo..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="space-y-3">
              {nuclei.length > 0 ? (
                [...nuclei]
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .filter((n) => n.name.toLowerCase().includes(searchQuery.toLowerCase()) || n.abbreviation.toLowerCase().includes(searchQuery.toLowerCase()))
                  .map((n) => (
                  <div
                    key={n.id}
                    onClick={() => navigate(`/geral/nucleos/${n.id}`)}
                    className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center overflow-hidden border-2 border-teal-500 flex-shrink-0">
						<span className="text-teal-600 font-bold text-sm">{n.abbreviation}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-teal-600 font-bold text-lg">{n.abbreviation}</span>
                        <span className="text-gray-400">|</span>
                        <span className="text-gray-800 font-medium">{n.name}</span>
                      </div>
                    </div>
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

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Núcleo</h2>

            <div className="space-y-4">
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
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewNucleusAbbreviation('');
                  setNewNucleusName('');
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
