import { useState } from "react";
import HelpTooltip from '../../components/HelpTooltip';
import { useNotification } from "../../contexts/NotificationProvider";
import { modalitiesApi, type ModalityListItem } from "../../api/modalities";
import { modalityTypesApi } from "../../api/modality-types";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import ChoseOneInput from "../utils/inputs/ChoseOneInput";
import { useSeason } from "../../contexts/SeasonContext";

const ModalityCreateModal = ({
  onCreate,
}: {
  onCreate?: (modality: ModalityListItem) => void;
}) => {

  const { notify } = useNotification();
  const { popModal } = useModal();
  const { loadedSeasonIsTheCurrentSeason, activeSeason } = useSeason();

  const [newModalityName, setNewModalityName] = useState("");
  const [modalityType, setModalityType] = useState("");

  const onClose = () => {
    setNewModalityName("");
    setModalityType("");
    popModal();
  };

  const handleAddModality = async () => {
    if (!newModalityName.trim()) {
      notify("Por favor, preencha o nome da modalidade.", 'error');
      return;
    }

    if (!modalityType) {
      notify("Por favor, selecione o tipo.", 'error');
      return;
    }

    try {
      const newModality = await modalitiesApi.create({
        name: newModalityName,
        modality_type_id: modalityType,
      });

      if (onCreate) onCreate(newModality);

      // Reset
      setNewModalityName("");
      setModalityType("");
      if (onClose) onClose();
      notify("Modalidade criada com sucesso!", 'success');
    } catch (err) {
      console.error("Failed to create modality:", err);
      notify("Não foi possível criar a modalidade. Verifique os dados e tente novamente.", 'error');
    }
  };

  return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Adicionar Modalidade
        </h2>

        { !loadedSeasonIsTheCurrentSeason && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-6" role="alert">
            <p>Esta modalidade será adicionada à temporada ativa: <strong>{activeSeason?.name}</strong></p>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome da Modalidade <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={newModalityName}
              onChange={(e) => setNewModalityName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Digite o nome"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Tipo <HelpTooltip text="Classifica a modalidade como individual (atletas competem individualmente, ex: atletismo) ou coletiva (equipas competem entre si, ex: futebol)." className="ml-1" /> <span className="text-red-500">*</span>
            </label>
            <ChoseOneInput
              allElementsLoader={() => modalityTypesApi.getAllMinimal({
                season_id: loadedSeasonIsTheCurrentSeason ? undefined : activeSeason?.id, mode: 'modality'
              }).then(types => types.map(type => ({ id: type.id, title: type.name })))}
              onSelect={(ele) => setModalityType(ele?.id || "")}
            />
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button
            onClick={() => {
              setNewModalityName("");
              setModalityType("");
              if (onClose) onClose();
            }}
            type="secondary"
            flexible={true}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleAddModality}
            type="primary"
            flexible={true}
          >
            Adicionar
          </Button>
        </div>
      </div>
  );
};

export default ModalityCreateModal;
