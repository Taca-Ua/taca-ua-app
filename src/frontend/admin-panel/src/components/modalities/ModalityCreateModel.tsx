import { useState, useEffect } from "react";
import HelpTooltip from '../../components/HelpTooltip';
import { useNotification } from "../../contexts/NotificationProvider";
import { modalitiesApi, type ModalityListItem } from "../../api/modalities";
import { modalityTypesApi, type ModalityTypeMinimal } from "../../api/modality-types";
import { btn } from '../../styles/buttonStyles';

const ModalityCreateModel = ({
  onCreate,
  onClose,
}: {
  onCreate?: (modality: ModalityListItem) => void;
  onClose?: () => void;
}) => {

  const [availableModalityTypes, setAvailableModalityTypes] = useState<ModalityTypeMinimal[]>([]);

  const [newModalityName, setNewModalityName] = useState("");
  const [modalityType, setModalityType] = useState("");
  const { notify } = useNotification();

  // Fetch modality types on mount if empty
  useEffect(() => {
    const fetchModalityTypes = async () => {
      try {
        const data = await modalityTypesApi.getAllMinimal();
        setAvailableModalityTypes(data);
      } catch (err) {
        console.error("Failed to fetch modality types:", err);
      }
    };

    if (availableModalityTypes.length === 0) {
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

      if (onCreate) onCreate(newModality);

      // Reset
      setNewModalityName("");
      setModalityType("");
      if (onClose) onClose();
      notify("Modalidade criada com sucesso!", 'success');
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
              {availableModalityTypes.sort((a, b) => a.name.localeCompare(b.name)).map((type) => (
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
              setNewModalityName("");
              setModalityType("");
              if (onClose) onClose();
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

export default ModalityCreateModel;
