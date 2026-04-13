import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { type NucleoDetail, nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import { btn } from "../../styles/buttonStyles";

const NucleusEditModel = ( {
  controller,
  onSave,
  nucleusData
} : {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
  onSave: (nucleus: NucleoDetail) => void,
  nucleusData?: NucleoDetail
}) => {
  // Extract nucleus ID from URL parameters
  const nucleusId = useParams<{ id: string }>().id;
  if (!nucleusId) {
    return null;
  }

  const [isOpen, setIsOpen] = controller;

  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');

  useEffect(() => {
    if (nucleusData) {
      setEditedAbbreviation(nucleusData.abbreviation);
      setEditedName(nucleusData.name);
      return;
    }

    const fetchNucleus = async () => {
      try {
        const data = await nucleosApi.getById(nucleusId);
        setEditedAbbreviation(data.abbreviation);
        setEditedName(data.name);
      } catch (error) {
        console.error("Error fetching nucleus details:", error);
      }
    };

    fetchNucleus();
  }, [nucleusData]);


  const onClose = () => {
    setEditedAbbreviation(nucleusData?.abbreviation || '');
    setEditedName(nucleusData?.name || '');
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

    try {
      const updatedNucleus = await nucleosApi.update(String(nucleusId), {
        abbreviation: editedAbbreviation,
        name: editedName,
      });
      onSave(updatedNucleus);
      setIsOpen(false);
    } catch (error) {
      console.error("Error updating nucleus:", error);
      alert('Ocorreu um erro ao atualizar o núcleo. Tente novamente.');
    };
  };

  if (!isOpen) {
      return null;
  }

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
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md`}
          >
            Cancelar
          </button>

          <button
            onClick={handleSave}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md`}
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

export default NucleusEditModel;
