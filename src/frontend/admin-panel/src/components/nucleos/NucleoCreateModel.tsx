import { useState } from "react";
import { nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";

const NucleoCreateModel = ({
  controller,
  onCreate,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  onCreate?: (nucleus: any) => void;
}) => {
  const [isOpen, setIsOpen] = controller;

  const [newNucleusAbbreviation, setNewNucleusAbbreviation] = useState("");
  const [newNucleusName, setNewNucleusName] = useState("");

  const handleCreateNucleus = async () => {
    if (!newNucleusAbbreviation.trim()) {
      alert("Por favor, preencha a abreviatura do núcleo.");
      return;
    }
    if (!newNucleusName.trim()) {
      alert("Por favor, preencha o nome do núcleo.");
      return;
    }
    try {
      const newNucleus = await nucleosApi.create({
        name: newNucleusName,
        abbreviation: newNucleusAbbreviation,
      });
      if (onCreate) onCreate(newNucleus);

      onClose();
    } catch (err) {
      console.error("Failed to create nucleus:", err);
      alert("Não foi possível criar o núcleo. Verifique os dados introduzidos e tente novamente.");
    }
  };

  const onClose = () => {
    setIsOpen(false);
    setNewNucleusAbbreviation("");
    setNewNucleusName("");
  }

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Núcleo
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Abreviatura{" "}
              <HelpTooltip
                text="Sigla ou código curto do núcleo, ex: NEECT, NEEEC. Utilizado como identificador visual nos perfis."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={newNucleusAbbreviation}
              onChange={(e) => setNewNucleusAbbreviation(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Ex: MECT, LEI, LECI"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome do Núcleo <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={newNucleusName}
              onChange={(e) => setNewNucleusName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Digite o nome completo"
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
            onClick={handleCreateNucleus}
            type="primary"
            flexible={true}
          >
            Adicionar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NucleoCreateModel;
