import { useState } from "react";
import { useModal } from "../../contexts/ModalContext";
import Button from "../utils/Button";
import FileInput from "../utils/inputs/FileInput";

const HeroImageInputModal = ({
    onImageSelected
}: {
    onImageSelected: (imageFile: File | null) => void
}) => {
    const { popModal } = useModal();

    const [imageFile, setImageFile] = useState<File | null>(null);

    const onSubmit = () => {
        if (imageFile) {
            onImageSelected(imageFile);
        }
        popModal();
    }

    return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[700px]">
        <h2 className="text-2xl font-bold mb-4">Selecionar Imagem de Fundo</h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">
            Imagem
          </label>
          <FileInput fileState={[imageFile, setImageFile]} fileType="image" />
        </div>
        <div className="flex justify-end gap-4 mt-6">
          <Button onClick={onSubmit} type="primary">
            Salvar
          </Button>
          <Button onClick={popModal} type="secondary">
            Cancelar
          </Button>
        </div>
      </div>
    );
}

export default HeroImageInputModal;
