import { useState, useMemo, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Modality {
  id: number;
  name: string;
  year: string;
  type: 'coletiva' | 'individual' | 'mista';
  scoring_schema?: string;
}

const mockModalities: Modality[] = [
  { id: 1, name: 'Futebol', year: '25/26', type: 'coletiva', scoring_schema: '{"win":3}' },
  { id: 2, name: 'Basquetebol', year: '25/26', type: 'coletiva' },
  { id: 3, name: 'Voleibol', year: '25/26', type: 'coletiva' },
  { id: 4, name: 'Futsal', year: '25/26', type: 'coletiva' },
  { id: 5, name: 'Andebol', year: '25/26', type: 'coletiva' },
  { id: 6, name: 'Rugby', year: '24/25', type: 'coletiva' },
];

const types = ['coletiva', 'individual', 'mista'];
const years = ['25/26', '24/25', '23/24', '22/23'];

const ModalityDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const initialModality = useMemo(
    () => mockModalities.find((m) => m.id === Number(id)) || null,
    [id]
  );

  const [modality, setModality] = useState<Modality | null>(initialModality);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedYear, setEditedYear] = useState('');
  const [editedType, setEditedType] = useState('');
  const [editedScoring, setEditedScoring] = useState('');

  useEffect(() => {
    if (!initialModality) navigate('/geral/modalidades');
  }, [initialModality, navigate]);

  if (!modality) return null;

  const handleEdit = () => {
    setEditedName(modality.name);
    setEditedYear(modality.year);
    setEditedType(modality.type);
    setEditedScoring(modality.scoring_schema || '');
    setIsEditModalOpen(true);
  };

  const handleSave = () => {
    setModality({
      ...modality,
      name: editedName,
      year: editedYear,
      type: editedType as 'coletiva' | 'individual' | 'mista',
      scoring_schema: editedScoring || undefined,
    });

    setIsEditModalOpen(false);
  };

  const handleDelete = () => {
    if (window.confirm(`Tem certeza que deseja eliminar "${modality.name}"?`)) {
      navigate('/geral/modalidades');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8">
        <div className="max-w-4xl mx-auto">

          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes da Modalidade</h1>

            <button
              onClick={() => navigate('/geral/modalidades')}
              className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
            >
              Voltar
            </button>
          </div>

          {/* Card */}
          <div className="bg-white rounded-lg shadow-md p-6 space-y-6">

            {/* Nombre */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {modality.name}
              </div>
            </div>

            {/* Año */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Época</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {modality.year}
              </div>
            </div>

            {/* Tipo */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Tipo</label>
              <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                {modality.type}
              </div>
            </div>

            {/* Scoring Schema */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Scoring Schema</label>
              <pre className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800 min-h-[100px] whitespace-pre-wrap">
                {modality.scoring_schema || '—'}
              </pre>
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

      {/* MODAL DE EDICIÓN */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">

            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Modalidade</h2>

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

              {/* TYPE */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <select
                  value={editedType}
                  onChange={(e) => setEditedType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Tipo</option>
                  {types.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              {/* SCORING SCHEMA */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">Scoring Schema (JSON)</label>
                <textarea
                  value={editedScoring}
                  onChange={(e) => setEditedScoring(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md min-h-[120px] focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
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

export default ModalityDetails;
