import { useState } from 'react';
import { modalityTypesApi } from '../../api/modality-types';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import HelpTooltip from '../HelpTooltip';
import Button from '../utils/Button';
import { useNotification } from '../../contexts/NotificationProvider';
import { useModal } from '../../contexts/ModalContext';
import ChoseOneInput from '../utils/inputs/ChoseOneInput';
import { useSeason } from '../../contexts/SeasonContext';
import { regulationsApi } from '../../api/regulations';

const definedPointUnitOptions = [
  { id: "points", title: "Ponto" },
  { id: "gol", title: "Golo" },
  { id: "set", title: "Set" },
];

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
  const { loadedSeason } = useSeason();

  const [editedName, setEditedName] = useState(modalityData.name);
  const [editedType, setEditedType] = useState(modalityData.modality_type?.id);
  const [editedRegulation, setEditedRegulation] = useState<string| null>(null);

  const [selectedPointUnit, setSelectedPointUnit] = useState(
    definedPointUnitOptions.some(option => option.id === modalityData.point_unit)
      ? modalityData.point_unit
      : "other"
  );
  const [editedPointUnit, setEditedPointUnit] = useState(modalityData.point_unit);

  const onClose = () => {
    setEditedName(modalityData.name);
    setEditedType(modalityData.modality_type?.id);
    popModal();
  }

  const handleSave = () => {
    modalitiesApi.update(modalityData.id, {
      name: editedName !== modalityData.name ? editedName : undefined,
      modality_type_id: editedType !== modalityData.modality_type?.id ? editedType : undefined,
      season_id: (editedType !== modalityData.modality_type?.id && modalityData.belongs_to_season) ? loadedSeason?.id : undefined,
      point_unit: selectedPointUnit === "other" ? editedPointUnit : selectedPointUnit,
    }, loadedSeason?.id).then((updatedModality) => {
      setModalityData(updatedModality);
      onClose();
      if (onSave) onSave(updatedModality);
      notify('Modalidade atualizada com sucesso!', 'success');
    }).catch((error) => {
      console.error('Error updating modality:', error);
      notify('Modalidade não atualizada. Tente novamente.', 'error');
    });

    if (editedRegulation !== null) {
      if (!loadedSeason) {
        notify('Temporada não carregada. Não foi possível atualizar o regulamento.', 'error');
        return;
      }

      modalitiesApi.updateRegulation(modalityData.id, {
        regulation_id: editedRegulation,
        season_id: loadedSeason.id
      }).then(() => {
        notify('Regulamento atualizado com sucesso!', 'success');
      }).catch((error) => {
        console.error('Error updating regulation:', error);
        notify('Regulamento não atualizado. Tente novamente.', 'error');
      });
    }
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
          {modalityData.belongs_to_season && (
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
                allElementsLoader={() => modalityTypesApi.getAllMinimal({
                  season_id: modalityData.belongs_to_season ? loadedSeason?.id : undefined, mode: 'modality'
                }).then(types => types.map(type => ({ id: type.id, title: type.name })))}
                onSelect={(ele) => setEditedType(ele?.id || "")}
                initialElement={modalityData.modality_type ? { id: modalityData.modality_type.id, title: modalityData.modality_type.name } : undefined}
              />
            </div>
          )}
          {modalityData.belongs_to_season && (<div>
            <label className="block text-gray-700 font-medium mb-2">
              Regulamento{" "}
              <HelpTooltip
                text="O regulamento define as regras específicas da modalidade, como critérios de desempate, pontuação e formato de competição. Ele é essencial para garantir que a modalidade seja conduzida de acordo com as diretrizes estabelecidas."
                className="ml-1"
              />
            </label>
            <ChoseOneInput
              allElementsLoader={() => regulationsApi.getAll({
                season_id: loadedSeason?.id,
              }).then(regs => regs.map(reg => ({ id: reg.id, title: reg.title, subtitle: reg.file_url })))}
              onSelect={(ele) => {
                setEditedRegulation(ele?.id || null);
              }}
              initialElement={modalityData.regulation ? { id: modalityData.regulation.id, title: modalityData.regulation.name, subTitle: modalityData.regulation.link } : undefined}
            />
          </div>)}

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Unidade de Pontuação <HelpTooltip text="Define a unidade de pontuação da modalidade, ou seja, o que é considerado um ponto. Ex: Golo, Set, Ponto." className="ml-1" />
            </label>
              <select
                value={selectedPointUnit || ""}
                onChange={(e) => {
                  setSelectedPointUnit(e.target.value)
                  if (e.target.value === "other") {
                    setEditedPointUnit("");
                  } else {
                    setEditedPointUnit(e.target.value);
                  }
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="">Selecione uma unidade</option>
                <option value="point">Ponto</option>
                <option value="gol">Golo</option>
                <option value="set">Set</option>
                <option value="other">Outro</option>
            </select>
            {selectedPointUnit === "other" && (
              <input
                type="text"
                value={editedPointUnit}
                onChange={(e) => setEditedPointUnit(e.target.value)}
                placeholder="Digite a unidade de pontuação"
                className="w-full mt-2 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            )}
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
