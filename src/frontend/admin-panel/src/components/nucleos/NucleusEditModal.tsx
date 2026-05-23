import { useEffect, useState, useRef } from "react";
import { type NucleoDetail, nucleosApi } from "../../api/nucleos";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";

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
  const { isAdminGeneral } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [editedAbbreviation, setEditedAbbreviation] = useState('');
  const [editedName, setEditedName] = useState('');
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  useEffect(() => {
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
    if (nucleus.logo_url) {
      setLogoPreview(nucleus.logo_url);
    }
  }, [nucleus]);


  const onClose = () => {
    setEditedAbbreviation(nucleus.abbreviation);
    setEditedName(nucleus.name);
    setLogoFile(null);
    setLogoPreview(nucleus.logo_url || null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    popModal();
  }

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
      image: logoFile || undefined,
    }).then((updatedNucleus) => {
      // Add cache-busting query parameter to logo URL to force refresh
      if (updatedNucleus.logo_url) {
        updatedNucleus.logo_url = `${updatedNucleus.logo_url}?t=${Date.now()}`;
      }
      setNucleus(updatedNucleus);
      if (onSave) onSave(updatedNucleus);
      popModal();
      notify('Núcleo atualizado com sucesso!', 'success');
    }).catch((error) => {
      console.error("Error updating nucleus:", error);
      notify('Ocorreu um erro ao atualizar o núcleo. Tente novamente.', 'error');
    });
  };

  if (!isAdminGeneral) return null;  // extra layer of protection, button should be hidden in the first place

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
