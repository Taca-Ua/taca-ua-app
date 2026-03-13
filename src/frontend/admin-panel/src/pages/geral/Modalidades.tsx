import { useState, useEffect } from "react";
import HelpTooltip from '../../components/HelpTooltip';
import { useNavigate } from "react-router-dom";
import Sidebar from "../../components/geral_navbar";
import { useNotification } from "../../contexts/NotificationProvider";
import { modalitiesApi, type Modality } from "../../api/modalities";
import { modalityTypesApi, type ModalityTypeMinimal } from "../../api/modality-types";
import { btn } from '../../styles/buttonStyles';

const MoadlitiesList = (modalities: Modality[]) => {
  if (modalities.length === 0) {
    return (
      <p className="text-gray-500 text-center py-8">
        Nenhuma modalidade encontrada.
      </p>
    );
  }

  const ModalityEntry = (mod: Modality) => {
    const navigate = useNavigate();
    return (
      <button
        type="button"
        onClick={() => navigate(`/geral/modalidades/${mod.id}`)}
        className="w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors flex justify-between items-center focus:outline-none focus:ring-2 focus:ring-teal-500"
      >
        <span className="text-gray-800 font-medium">{mod.name}</span>
        <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
          {mod.modality_type.name}
        </span>
      </button>
    );
  };

  return (
    <div className="space-y-3">
      {modalities.map((mod) => (
        <ModalityEntry key={mod.id} {...mod} />
      ))}
    </div>
  );
};

const CreateModalityModal = ({
  modalityTypes,
  setModalityTypes,
  addModality,
  onClose,
}: {
  modalityTypes: ModalityTypeMinimal[];
  setModalityTypes: React.Dispatch<React.SetStateAction<ModalityTypeMinimal[]>>;
  addModality: (modality: Modality) => void;
  onClose: () => void;
}) => {
  const [newModalityName, setNewModalityName] = useState("");
  const [modalityType, setModalityType] = useState("");
  const { notify } = useNotification();

  // Fetch modality types on mount if empty
  useEffect(() => {
    const fetchModalityTypes = async () => {
      try {
        const data = await modalityTypesApi.getAllMinimal();
        setModalityTypes(data);
      } catch (err) {
        console.error("Failed to fetch modality types:", err);
      }
    };

    if (modalityTypes.length === 0) {
      fetchModalityTypes();
    }
  }, []);

  const handleAddModality = async () => {
    if (!newModalityName.trim()) {
      notify("Por favor, preencha o nome da modalidade.", 'error');
      return;
    }

    if (!modalityType) {
      notify("Por favor, selecione o tipo.", 'error');
      return;
    }

    try {
      const newModality = await modalitiesApi.create({
        name: newModalityName,
        modality_type_id: modalityType,
      });

      addModality(newModality);

      // Reset
      setNewModalityName("");
      setModalityType("");
      onClose();
    } catch (err) {
      console.error("Failed to create modality:", err);
      notify("Não foi possível criar a modalidade. Verifique os dados e tente novamente.", 'error');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Modalidade
        </h2>

        <div className="space-y-4">
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

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Tipo <HelpTooltip text="Classifica a modalidade como individual (atletas competem individualmente, ex: atletismo) ou coletiva (equipas competem entre si, ex: futebol)." className="ml-1" /> <span className="text-red-500">*</span>
            </label>
            <select
              value={modalityType}
              onChange={(e) => setModalityType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Selecionar Tipo</option>
              {modalityTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={() => {
              onClose();
              setNewModalityName("");
              setModalityType("");
            }}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium transition-colors`}
          >
            Cancelar
          </button>
          <button
            onClick={handleAddModality}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
          >
            Adicionar
          </button>
        </div>
      </div>
    </div>
  );
};

const Modalities = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const [modalities, setModalities] = useState<Modality[]>([]);
  const [modalityTypes, setModalityTypes] = useState<ModalityTypeMinimal[]>([]);

  // Fetch modalities on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await modalitiesApi.getAll();
        setModalities(data);
      } catch (err) {
        console.error("Failed to fetch modalities:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const addModality = (modality: Modality) => {
    setModalities([...modalities, modality]);
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
            <h1 className="text-3xl font-bold text-gray-800">Modalidades</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2`}
            >
              <span>+</span>
              Adicionar Modalidade
            </button>
          </div>

          <div className="mb-6 flex gap-3">
            <input
              type="text"
              placeholder="Pesquisar modalidade..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="">Todos os tipos</option>
              {[...new Map(modalities.map(m => [m.modality_type.id, m.modality_type])).values()]
                .sort((a, b) => a.name.localeCompare(b.name))
                .map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
            </select>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            {MoadlitiesList(
              [...modalities]
                .sort((a, b) => a.name.localeCompare(b.name))
                .filter((m) =>
                  m.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
                  (typeFilter === '' || m.modality_type.id === typeFilter)
                )
            )}
          </div>
        </div>
      </div>

      {isModalOpen && (
        <CreateModalityModal
          modalityTypes={modalityTypes}
          setModalityTypes={setModalityTypes}
          addModality={addModality}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </div>
  );
};

export default Modalities;
