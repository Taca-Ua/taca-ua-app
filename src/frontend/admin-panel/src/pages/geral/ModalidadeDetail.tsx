import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from '../../components/geral_navbar';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import { modalityTypesApi } from '../../api/modality-types';

interface ModalityType {
	  id: string;
	  name: string;
}

const ModalidadeDetailEditModal = ({
  onClose,  // Function to close the modal
  modality,  // Current modality data
  setModality,  // Function to update modality state
  modalityTypes,  // List of modality types
  setModalityTypes  // Function to set modality types
}: {
  onClose: () => void;
  modality: ModalityDetail;
  setModality: React.Dispatch<React.SetStateAction<ModalityDetail | null>>;
  modalityTypes: ModalityType[];
  setModalityTypes: React.Dispatch<React.SetStateAction<ModalityType[]>>;
}) => {
  const [error, setError] = useState('');
  const [editedName, setEditedName] = useState(modality.name);
  const [editedType, setEditedType] = useState(modality.modality_type.id);

  // Fetch modality types if not already loaded
  useEffect(() => {
    const fetchModalityTypes = async () => {
      try {
      const data = await modalityTypesApi.getAll();
      setModalityTypes(data);
      } catch (err) {
      console.error('Failed to fetch modality types:', err);
      }
	};
  if (modalityTypes.length === 0) {
	  fetchModalityTypes();
  }
  }, []);

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
      const updatedModality = await modalitiesApi.update(String(modality.id), {
        name: editedName,
        modality_type_id: editedType,
      });
      setModality(updatedModality);
      setError('');
      onClose();
    } catch (err) {
      console.error('Failed to update modality:', err);
      setError('Erro ao atualizar modalidade');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
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
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={onClose}
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
  ); // Modal implementation is now in the main component
};


function ModalidadeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modality, setModality] = useState<ModalityDetail | null>(null);
  const [modalityTypes, setModalityTypes] = useState<ModalityType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await modalitiesApi.getById(String(id));
        setModality(data);
      } catch (err) {
        console.error('Failed to fetch modality:', err);
        navigate('/geral/modalidades');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate]);

  const handleEdit = () => {
    if (!modality) return;
    setIsModalOpen(true);
  };

  const handleDelete = async () => {
    if (window.confirm('Tem certeza que deseja eliminar esta modalidade?')) {
      try {
        await modalitiesApi.delete(String(id));
        navigate('/geral/modalidades');
      } catch (err) {
        console.error('Failed to delete modality:', err);
        alert('Erro ao eliminar modalidade');
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

      {/* Content */}
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
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800 capitalize">{modality.modality_type.name}</div>
            </div>
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
        <ModalidadeDetailEditModal
          onClose={() => setIsModalOpen(false)}
          modality={modality}
          setModality={setModality}
          modalityTypes={modalityTypes}
          setModalityTypes={setModalityTypes}
        />
      )}
    </div>
  );
}

export default ModalidadeDetail;
