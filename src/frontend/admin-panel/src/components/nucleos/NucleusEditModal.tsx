import { useEffect, useState } from "react";
import { type NucleoDetail, nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";

const NucleusEditModal = ( {
  controller,
  nucleusState,
  onSave,
} : {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
  nucleusState: [NucleoDetail, React.Dispatch<React.SetStateAction<NucleoDetail | null>>],
  onSave?: (updatedNucleus: NucleoDetail) => void,
}) => {

  const [isOpen, setIsOpen] = controller;
  const [nucleus, setNucleus] = nucleusState;
  const { notify } = useNotification();

  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');

  useEffect(() => {
    if (!isOpen) return;

    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
  }, [isOpen]);


  const onClose = () => {
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
    setIsOpen(false);
  }

  const handleSave = async () => {
    if (!editedAbbreviation.trim()) {
      alert('Abreviatura é obrigatória');
      return;
    }
    if (!editedName.trim()) {
      alert('Nome é obrigatório');
      return;
    }

    nucleosApi.update(nucleus.id, {
      abbreviation: editedAbbreviation,
      name: editedName,
    }).then((updatedNucleus) => {
      setNucleus(updatedNucleus);
      if (onSave) onSave(updatedNucleus);
      setIsOpen(false);
      notify('Núcleo atualizado com sucesso!', 'success');
    }).catch((error) => {
      console.error("Error updating nucleus:", error);
      notify('Ocorreu um erro ao atualizar o núcleo. Tente novamente.', 'error');
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Núcleo</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Abreviatura{" "}
              <HelpTooltip
                text="Sigla ou código curto do núcleo. Utilizado como identificador visual."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={editedAbbreviation}
              onChange={(e) => setEditedAbbreviation(e.target.value)}
              placeholder="Ex: MECT, LEI, LECI"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              placeholder="Digite o nome completo"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button
            onClick={onClose}
            type="secondary"
            flexible={true}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSave}
            type="primary"
            flexible={true}
          >
            Guardar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NucleusEditModal;
