import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../utils/Button';
import ModalityEditModal from './ModalityEditModel';
import { useModal } from '../../contexts/ModalContext';
import { useSeason } from '../../contexts/SeasonContext';
import ChoseOneModal from '../utils/costum_menus/ChoseOneModal';
import { modalityTypesApi } from '../../api/modality-types';
import { useNotification } from '../../contexts/NotificationProvider';


const ModalityInfoComponent = ( {
  modalityState
} : {
  modalityState: [ModalityDetail, React.Dispatch<React.SetStateAction<ModalityDetail | null>>]
}) => {
  const navigate = useNavigate();
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();
  const { loadedSeason } = useSeason();
  const { notify } = useNotification();

  const [modality, setModality] = modalityState;

  const handleDelete = async () => {
    try {
      await modalitiesApi.delete(modality.id);
      navigate('/modalidades');
    } catch (error) {
      console.error('Error deleting modality:', error);
    }
  };

  const handleRemoveFromSeason = () => {
    if (!loadedSeason) return;
    modalitiesApi.removeFromSeason(modality.id, loadedSeason.id)
      .then((updatedModality) => {
        setModality(updatedModality);
        notify('Modalidade removida da temporada com sucesso.', 'success');
      }).catch((error) => {
        notify('Falha ao remover modalidade da temporada.', 'error');
        console.error('Error removing modality from season:', error);
      });
  };

  const handleAddToSeason = (modalityTypeId: string | undefined) => {
    if (!modalityTypeId) return; // Should not happen, but just in case

    modalitiesApi.update(modality.id, {
      season_id: loadedSeason?.id,
      modality_type_id: modalityTypeId,
    }).then((updatedModality) => {
      setModality(updatedModality);
      notify('Modalidade adicionada à temporada com sucesso.', 'success');
    }).catch((error) => {
      notify('Falha ao adicionar modalidade à temporada.', 'error');
      console.error('Error adding modality to season:', error);
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8 mb-6">
      <div className="space-y-6">
        <div>
          <label className="block text-teal-500 font-medium mb-2">Nome</label>
          <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
            {modality.name}
          </div>
        </div>
        <div>
          <label className="block text-teal-500 font-medium mb-2">Tipo</label>
          <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800 capitalize">
            {modality.modality_type?.name || "N/A"}
          </div>
        </div>
      </div>

      <div className="flex gap-4 mt-8">
        <Button
          onClick={() =>
            pushModal(
              <ModalityEditModal modalityState={[modality, setModality]} />,
            )
          }
          type="primary"
          active={isAdminGeneral}
          flexible={true}
        >
          Editar
        </Button>
        <Button
          onClick={() =>
            pushModal(
              <ChoseOneModal
                title={`Escolha formato de prova`}
                allElementsLoader={() => modalityTypesApi
                  .getAllMinimal({
                    season_id: loadedSeason?.id,
                    mode: 'modality'
                  })
                  .then((types) =>
                    types.map((type) => ({ id: type.id, title: type.name })),
                  )}
                onSelect={(type) => handleAddToSeason(type?.id)}
                hideClearButton={true}
              />,
            )
          }
          type="info"
          active={isAdminGeneral && !modality.belongs_to_season}
          flexible={true}
        >
          Adicionar à Temporada
        </Button>
        <Button
          onClick={handleRemoveFromSeason}
          type="danger"
          active={isAdminGeneral && modality.belongs_to_season}
          confirmation={{
            title: "Remover modalidade da temporada " + loadedSeason?.name,
            message:
              "Tem certeza que deseja remover esta modalidade da temporada? Os torneios, jogos e equipas associados desta modalidade desta temporada serão apagados. Esta ação não pode ser desfeita.",
            confirmLabel: "Remover",
          }}
          flexible={true}
        >
          Remover da Temporada
        </Button>
      </div>
    </div>
  );
};

export default ModalityInfoComponent;
