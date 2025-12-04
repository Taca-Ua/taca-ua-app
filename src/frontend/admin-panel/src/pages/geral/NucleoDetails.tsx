import { useState, useMemo, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Nucleos {
  id: number;
  name: string;
  year: string;
}

// Mock de núcleos
const mockNucleo: Nucleos[] = [
  { id: 1, name: 'Núcleo A', year: '25/26' },
  { id: 2, name: 'Núcleo B', year: '25/26' },
  { id: 3, name: 'Núcleo C', year: '24/25' },
  { id: 4, name: 'Núcleo D', year: '23/24' },
];

const years = ['25/26', '24/25', '23/24', '22/23'];

const NucleoDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const initialNucleus = useMemo(
    () => mockNucleo.find((n) => n.id === Number(id)) || null,
    [id]
  );

  const [nucleus, setNucleus] = useState<Nucleos | null>(initialNucleus);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedYear, setEditedYear] = useState('');

  useEffect(() => {
    if (!initialNucleus) navigate('/geral/nucleos');
  }, [initialNucleus, navigate]);

  if (!nucleus) return null;

  const handleEdit = () => {
    setEditedName(nucleus.name);
    setEditedYear(nucleus.year);
    setIsEditModalOpen(true);
  };

  const handleSave = () => {
    setNucleus({
      ...nucleus,
      name: editedName,
      year: editedYear,
    });
    setIsEditModalOpen(false);
  };

  const handleDelete = () => {
    if (window.confirm(`Tem certeza que deseja eliminar "${nucleus.name}"?`)) {
      navigate('/geral/nucleos');
    }
  };

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

            {/* Nome */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {nucleus.name}
              </div>
            </div>

            {/* Year */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Época</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {nucleus.year}
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

            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Núcleo</h2>

            <div className="space-y-4">
              {/* NAME */}
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

              {/* YEAR */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Época <span className="text-red-500">*</span>
                </label>
                <select
                  value={editedYear}
                  onChange={(e) => setEditedYear(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Época</option>
                  {years.map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsEditModalOpen(false)}
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
