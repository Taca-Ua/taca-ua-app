import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from '../../components/geral_navbar';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { scoringFormatsApi } from '../../api/scoring-formats';

interface ModalityType {
	  id: string;
	  name: string;
}

function ModalidadeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modality, setModality] = useState<Modality | null>(null);
  const [modalityTypes, setModalityTypes] = useState<ModalityType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [editedName, setEditedName] = useState('');
  const [editedType, setEditedType] = useState('');
  const [editedScoringSchema, setEditedScoringSchema] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await modalitiesApi.getById(String(id));
        setModality(data);
        setError('');
      } catch (err) {
        console.error('Failed to fetch modality:', err);
        setError('Erro ao carregar modalidade');
        navigate('/geral/modalidades');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate]);

  useEffect(() => {
	const fetchModalityTypes = async () => {
	  try {
		const data = await scoringFormatsApi.getAll();
		setModalityTypes(data);
	  } catch (err) {
		console.error('Failed to fetch modality types:', err);
	  }
	};
	fetchModalityTypes();
  }, []);

  const handleEdit = () => {
    if (!modality) return;
    setEditedName(modality.name);
    setEditedType(modality.modality_type);
    setEditedScoringSchema(modality.scoring_schema ? JSON.stringify(modality.scoring_schema, null, 2) : '');
    setError('');
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!editedName.trim()) {
      setError('Nome é obrigatório');
      return;
    }
    if (!editedType) {
      setError('Tipo é obrigatório');
      return;
    }

    try {
      let scoringSchema: Record<string, number> | null = null;
      if (editedScoringSchema.trim()) {
        try {
          scoringSchema = JSON.parse(editedScoringSchema);
        } catch {
          setError('Scoring schema inválido. Use formato JSON válido.');
          return;
        }
      }

      const updatedModality = await modalitiesApi.update(String(id), {
        name: editedName,
        modality_type_id: editedType,
        scoring_schema: scoringSchema,
      });
      setModality(updatedModality);
      setError('');
      setIsModalOpen(false);
	  navigate(`/geral/modalidades/`);
    } catch (err) {
      console.error('Failed to update modality:', err);
      setError('Erro ao atualizar modalidade');
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Tem certeza que deseja eliminar esta modalidade?')) {
      try {
        await modalitiesApi.delete(String(id));
        navigate('/geral/modalidades');
      } catch (err) {
        console.error('Failed to delete modality:', err);
        setError('Erro ao eliminar modalidade');
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

  if (!modality) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="p-8 max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="space-y-6">
            {/* Name */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{modality.name}</div>
            </div>
            {/* Type */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Tipo</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800 capitalize">{modality.modality_type}</div>
            </div>
            {/* Scoring Schema */}
            {modality.scoring_schema && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Scoring Schema</label>
                <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800 font-mono text-sm">
                  {JSON.stringify(modality.scoring_schema, null, 2)}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={handleEdit} className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium">
              Editar
            </button>
            <button onClick={handleDelete} className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium">
              Eliminar
            </button>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Modalidade</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  placeholder="Digite o nome"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
              </div>
              {/* Type */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <select
                  value={editedType}
                  onChange={(e) => setEditedType(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Tipo</option>
                  {modalityTypes.map((type) => (
					<option key={type.id} value={type.id}>{type.name}</option>
				  ))}
                </select>
              </div>
              {/* Scoring Schema */}
              {/* <div>
                <label className="block text-gray-700 font-medium mb-2">Scoring Schema (JSON)</label>
                <textarea
                  value={editedScoringSchema}
                  onChange={(e) => setEditedScoringSchema(e.target.value)}
                  placeholder='{"win": 3, "draw": 1, "loss": 0}'
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 min-h-[100px] font-mono text-sm"
                />
              </div> */}
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
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
}

export default ModalidadeDetail;
