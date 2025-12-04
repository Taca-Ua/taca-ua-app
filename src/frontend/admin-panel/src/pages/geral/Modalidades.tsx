import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Modality {
  id: number;
  name: string;
  year: string;
  type: 'coletiva' | 'individual' | 'mista';
  scoring_schema?: string;
}

const Modalities = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newModalityName, setNewModalityName] = useState('');
  const [modalityType, setModalityType] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [newScoringSchema, setNewScoringSchema] = useState('');

  // Initial mock resplace for API data
  const [modalities, setModalities] = useState<Modality[]>([
    { id: 1, name: 'Futebol', year: '25/26', type: 'coletiva',scoring_schema: '{"win":3}' },
    { id: 2, name: 'Basquetebol', year: '25/26', type: 'coletiva' },
    { id: 3, name: 'Voleibol', year: '25/26', type: 'coletiva' },
    { id: 4, name: 'Futsal', year: '25/26', type: 'coletiva' },
    { id: 5, name: 'Andebol', year: '25/26', type: 'coletiva' },
    { id: 6, name: 'Rugby', year: '24/25', type: 'coletiva' },
  ]);

  const [filterYear, setFilterYear] = useState('');

  const years = ['25/26', '24/25', '23/24', '22/23'];

  const handleAddModality = () => {
    if (!newModalityName.trim()) {
      alert('Por favor, preencha o nome da modalidade.');
      return;
    }

    if (!selectedYear) {
      alert('Por favor, selecione uma época.');
      return;
    }

    if (!modalityType) {
      alert('Por favor, selecione o tipo.');
      return;
    }

    const newModality: Modality = {
      id: modalities.length + 1,
      name: newModalityName,
      year: selectedYear,
      type: modalityType as 'coletiva' | 'individual' | 'mista',
      scoring_schema: newScoringSchema || undefined,
    };

    setModalities([...modalities, newModality]);

    // Reset
    setNewModalityName('');
    setModalityType('');
    setSelectedYear('');
    setNewScoringSchema('');
    setIsModalOpen(false);
  };

  // Filtrado por época
  const filteredModalities = filterYear
    ? modalities.filter((m) => m.year === filterYear)
    : modalities;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Modalidades</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Modalidade
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

          {/* Modalities List */}
          <div className="bg-white rounded-lg shadow-md p-6">

            <div className="space-y-3">
              {filteredModalities.length > 0 ? (
                filteredModalities.map((mod) => (
                  <div
                    key={mod.id}
                    onClick={() => navigate(`/geral/modalidades/${mod.id}`)}
                    className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
                  >
                    <span className="text-gray-800 font-medium">{mod.name}</span>
                    <span className="text-gray-600 text-sm">
                      Época: {mod.year} | Tipo: {mod.type}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Nenhuma modalidade encontrada para esta época.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Modality Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Modalidade</h2>

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Nome da Modalidade <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newModalityName}
                  onChange={(e) => setNewModalityName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome"
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <select
                  value={modalityType}
                  onChange={(e) => setModalityType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Tipo</option>
                  <option value="coletiva">Coletiva</option>
                  <option value="individual">Individual</option>
                  <option value="mista">Mista</option>
                </select>
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

              {/* Scoring Schema (JSON) */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Scoring Schema (JSON)
                </label>
                <textarea
                  value={newScoringSchema}
                  onChange={(e) => setNewScoringSchema(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[100px]"
                  placeholder='{"win": 3, "draw": 1, "loss": 0}'
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewModalityName('');
                  setModalityType('');
                  setSelectedYear('');
                  setNewScoringSchema('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddModality}
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

export default Modalities;
