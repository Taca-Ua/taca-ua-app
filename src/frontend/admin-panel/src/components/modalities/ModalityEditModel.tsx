import { useState } from 'react';
import { modalityTypesApi } from '../../api/modality-types';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import HelpTooltip from '../HelpTooltip';
import Button from '../utils/Button';
import { useNotification } from '../../contexts/NotificationProvider';
import { useModal } from '../../contexts/ModalContext';
import ChoseOneInput from '../utils/inputs/ChoseOneInput';

const ModalityEditModal = ( {
  modalityState,
  onSave,
} : {
  modalityState: [ModalityDetail, React.Dispatch<React.SetStateAction<ModalityDetail | null>>],
  onSave?: (modality: ModalityDetail) => void,
}) => {

  const [modalityData, setModalityData] = modalityState;
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [editedName, setEditedName] = useState(modalityData.name);
  const [editedType, setEditedType] = useState(modalityData.modality_type.id);

  const onClose = () => {
    setEditedName(modalityData.name);
    setEditedType(modalityData.modality_type.id);
    popModal();
  }

  const handleSave = () => {
    modalitiesApi.update(modalityData.id, {
      name: editedName,
      modality_type_id: editedType,

    }).then((updatedModality) => {
      setModalityData(updatedModality);
      onClose();
      if (onSave) onSave(updatedModality);
      notify('Modalidade atualizada com sucesso!', 'success');
    }).catch((error) => {
      console.error('Error updating modality:', error);
      notify('Failed to update modality. Please try again.', 'error');
    });
  };

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Editar Modalidade
        </h2>

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
              Tipo{" "}
              <HelpTooltip
                text="Classifica a modalidade como individual (atletas competem individualmente) ou coletiva (equipas competem entre si). Afeta as regras de inscrição e pontuação."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <ChoseOneInput
              allElementsLoader={() => modalityTypesApi.getAll().then(types => types.map(type => ({ id: type.id, title: type.name })))}
              onSelect={(ele) => setEditedType(ele?.id || "")}
              initialElement={{ id: modalityData.modality_type.id, title: modalityData.modality_type.name }}
            />
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button onClick={onClose} type="secondary" flexible={true}>
            Cancelar
          </Button>
          <Button onClick={handleSave} type="primary" flexible={true}>
            Guardar
          </Button>
        </div>
      </div>
  );
};

export default ModalityEditModal;
