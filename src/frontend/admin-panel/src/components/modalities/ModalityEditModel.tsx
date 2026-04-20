import { useEffect, useState } from 'react';
import { modalityTypesApi } from '../../api/modality-types';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import HelpTooltip from '../HelpTooltip';
import Button from '../utils/Button';

const ModalityEditModel = ( {
  controller,
  onSave,
  modalityData,
  modalityId
} : {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
  onSave: (modality: ModalityDetail) => void,
  modalityData?: ModalityDetail,
  modalityId?: string
}) => {
  if (!modalityId && !modalityData) {
    throw new Error("ModalityEditModel requires either modalityId or modalityData");
  }

  modalityId = modalityId || modalityData!.id;  // Use the provided modalityId or extract it from modalityData

  // State to control modal visibility
  const [isOpen, setIsOpen] = controller;

  const [editedName, setEditedName] = useState('');
  const [editedType, setEditedType] = useState('');
  const [modalityTypes, setModalityTypes] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    if (!isOpen) {
      return;  // Only fetch modality types when the modal is opened
    }

    if (modalityTypes.length > 0) {
      return;  // Modality types are already fetched, no need to fetch again
    }

    const fetchModalityTypes = async () => {
      try {
        const data = await modalityTypesApi.getAll();
        setModalityTypes(data);
      } catch (error) {
        console.error('Error fetching modality types:', error);
      }
    };

    fetchModalityTypes();
  }, [isOpen]);

  useEffect(() => {
    if (modalityData) {
      setEditedName(modalityData.name);
      setEditedType(modalityData.modality_type.id);
      return;
    }

    const fetchModality = async () => {
      try {
        const data = await modalitiesApi.getById(modalityId);
        setEditedName(data.name);
        setEditedType(data.modality_type.id);
      } catch (error) {
        console.error('Error fetching modality:', error);
      }
    };

    console.log('Fetching modality with ID:', modalityId);
    fetchModality();
  }, [modalityId]);

  const onClose = () => {
    setEditedName(modalityData ? modalityData.name : '');
    setEditedType(modalityData ? modalityData.modality_type.id : '');
    setIsOpen(false);
  }

  const handleSave = async () => {
    try {
      let updatedModality = await modalitiesApi.update(modalityId, {
        name: editedName,
        modality_type_id: editedType,
      });
      onSave(updatedModality);
    } catch (error) {
      console.error('Error updating modality:', error);
    } finally {
      onClose();
    }
  };

  if (!isOpen) {
    return null;
  }
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Modalidade</h2>

        <div className="space-y-4">
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
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Tipo <HelpTooltip text="Classifica a modalidade como individual (atletas competem individualmente) ou coletiva (equipas competem entre si). Afeta as regras de inscrição e pontuação." className="ml-1" /> <span className="text-red-500">*</span>
            </label>
            <select
              value={editedType}
              onChange={(e) => setEditedType(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            >
              <option value="">Selecionar Tipo</option>
              {[...modalityTypes].sort((a, b) => a.name.localeCompare(b.name)).map((type) => (
      <option key={type.id} value={type.id}>{type.name}</option>
      ))}
            </select>
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button
            onClick={onClose}
            type='secondary'
            flexible={true}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSave}
            type='primary'
            flexible={true}
          >
            Guardar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModalityEditModel;
