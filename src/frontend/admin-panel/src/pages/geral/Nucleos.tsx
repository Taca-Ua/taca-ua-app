import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Nucleos {
  id: number;
  name: string;
  year: string;
}

const Nucleo = () => {
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newNucleusName, setNewNucleusName] = useState('');
  const [selectedYear, setSelectedYear] = useState('');

  const [nuclei, setNuclei] = useState<Nucleos[]>([
    { id: 1, name: 'Núcleo A', year: '25/26' },
    { id: 2, name: 'Núcleo B', year: '25/26' },
    { id: 3, name: 'Núcleo C', year: '24/25' },
    { id: 4, name: 'Núcleo D', year: '23/24' },
  ]);

  const [filterYear, setFilterYear] = useState('');

  const years = ['25/26', '24/25', '23/24', '22/23'];

  // Agregar nuevo núcleo
  const handleAddNucleus = () => {
    if (!newNucleusName.trim()) {
      alert('Por favor, preencha o nome do núcleo.');
      return;
    }

    if (!selectedYear) {
      alert('Por favor, selecione uma época.');
      return;
    }

    const newNucleus: Nucleos = {
      id: nuclei.length + 1,
      name: newNucleusName,
      year: selectedYear,
    };

    setNuclei([...nuclei, newNucleus]);

    // Reset
    setNewNucleusName('');
    setSelectedYear('');
    setIsModalOpen(false);
  };

  // Filtrado por época
  const filteredNuclei = filterYear
    ? nuclei.filter((n) => n.year === filterYear)
    : nuclei;

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

          {/* Year Filter */}
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">Época</label>
            <select
              value={filterYear}
              onChange={(e) => setFilterYear(e.target.value)}
              className="w-64 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Selecionar Época</option>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          {/* Nuclei List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Núcleos</h2>

            <div className="space-y-3">
              {filteredNuclei.length > 0 ? (
                filteredNuclei.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => navigate(`/geral/nucleos/${n.id}`)}
                    className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
                  >
                    <span className="text-gray-800 font-medium">{n.name}</span>
                    <span className="text-teal-600 text-sm font-medium">Época: {n.year}</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Nenhum núcleo encontrado para esta época.
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

            <div className="space-y-4">
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
                  placeholder="Digite o nome"
                />
              </div>

              {/* Year */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Época <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Época</option>
                  {years.map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewNucleusName('');
                  setSelectedYear('');
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
