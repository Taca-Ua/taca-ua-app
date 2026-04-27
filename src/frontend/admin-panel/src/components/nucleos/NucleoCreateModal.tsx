import { useState, useRef } from "react";
import { nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";

const NucleoCreateModal = ({
  onCreate,
}: {
  onCreate?: (nucleus: any) => void;
}) => {
  const { popModal } = useModal();
  const { isAdminGeneral } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [newNucleusAbbreviation, setNewNucleusAbbreviation] = useState("");
  const [newNucleusName, setNewNucleusName] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setLogoFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setLogoPreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveLogo = () => {
    setLogoFile(null);
    setLogoPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

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
        image: logoFile || undefined,
      });
      if (onCreate) onCreate(newNucleus);

      onClose();
    } catch (err) {
      console.error("Failed to create nucleus:", err);
      alert("Não foi possível criar o núcleo. Verifique os dados introduzidos e tente novamente.");
    }
  };

  const onClose = () => {
    popModal();
    setNewNucleusAbbreviation("");
    setNewNucleusName("");
    setLogoFile(null);
    setLogoPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  if (!isAdminGeneral) return null;  // extra layer of protection, button should be hidden in the first place

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
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

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Logo <span className="text-gray-400 text-sm">(opcional)</span>
            </label>
            <div className="flex items-center gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleLogoChange}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 border border-gray-300 rounded-md bg-white hover:bg-gray-50 cursor-pointer font-medium text-gray-700"
              >
                Escolher Logo
              </button>
              {logoFile && (
                <span className="text-sm text-gray-600">{logoFile.name}</span>
              )}
            </div>
            {logoPreview && (
              <div className="mt-3 relative">
                <img
                  src={logoPreview}
                  alt="Logo preview"
                  className="h-20 w-20 object-cover rounded-md border border-gray-200"
                />
                <button
                  type="button"
                  onClick={handleRemoveLogo}
                  className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center"
                >
                  ✕
                </button>
              </div>
            )}
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
  );
};

export default NucleoCreateModal;
