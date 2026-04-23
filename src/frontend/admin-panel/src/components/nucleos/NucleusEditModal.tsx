import { useEffect, useState } from "react";
import { type NucleoDetail, nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";
import { useModal } from "../../contexts/ModalContext";

const NucleusEditModal = ( {
  nucleusState,
  onSave,
} : {
  nucleusState: [NucleoDetail, React.Dispatch<React.SetStateAction<NucleoDetail | null>>],
  onSave?: (updatedNucleus: NucleoDetail) => void,
}) => {

  const [nucleus, setNucleus] = nucleusState;
  const { notify } = useNotification();
  const { popModal } = useModal();

  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');

  useEffect(() => {
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
  }, []);


  const onClose = () => {
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
    popModal();
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
      popModal();
      notify('Núcleo atualizado com sucesso!', 'success');
    }).catch((error) => {
      console.error("Error updating nucleus:", error);
      notify('Ocorreu um erro ao atualizar o núcleo. Tente novamente.', 'error');
    });
  };

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
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
  );
};

export default NucleusEditModal;
