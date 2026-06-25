import { useState } from "react";
import FileInput from "../utils/inputs/FileInput";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useNotification } from "../../contexts/NotificationProvider";

interface Sponsor {
    name: string;
    logo: string;
    link: string;
}

const AddSponsorModal = ({
    onCreate
} : {
    onCreate?: (sponsor: Sponsor) => void;
}) => {
    const { popModal } = useModal();
    const { notify } = useNotification();

    const [name, setName] = useState("");
    const [logo, setLogo] = useState<File | null>(null);
    const [link, setLink] = useState("");

    const handleCreate = () => {
        if (!name || !logo || !link) {
            notify("Por favor, preencha todos os campos.", "error");
            return;
        }
        if (onCreate) {
            onCreate({ name, logo: logo ? URL.createObjectURL(logo) : "", link });
        }
        onClose();
    };

    const onClose = () => {
        // Reset the form fields when closing the modal
        setName("");
        setLogo(null);
        setLink("");
        popModal();
    }

    return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[700px]">
        <h2 className="text-2xl font-bold mb-4">Adicionar Patrocinador</h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Nome</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Link</label>
          <input
            type="text"
            value={link}
            onChange={(e) => setLink(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Logo</label>
          <FileInput fileState={[logo, setLogo]} fileType="image" />
        </div>

        <div className="flex justify-end gap-4 mt-6">
          <Button onClick={handleCreate} type="primary" flexible={true}>
            Criar
          </Button>
          <Button onClick={onClose} type="secondary" flexible={true}>
            Cancelar
          </Button>
        </div>
      </div>
    );
};

export default AddSponsorModal
