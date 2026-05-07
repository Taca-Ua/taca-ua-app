import { useEffect, useState } from "react";
import { type ModalityListItem, modalitiesApi } from "../../api/modalities";
import ModalitiesListComponent from "../../components/modalities/ModalitiesListComponent";
import { useAuth } from "../../hooks/useAuth";
import Button from "../../components/utils/Button";
import ModalityCreateModal from "../../components/modalities/ModalityCreateModal";
import { useModal } from "../../contexts/ModalContext";
import { useNotification } from "../../contexts/NotificationProvider";
import { useSeason } from "../../contexts/SeasonContext";
import { useNavigate } from "react-router-dom";


const Modalities = () => {
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();
  const { notify } = useNotification();
  const { loadedSeason } = useSeason();
  const navigate = useNavigate();

  const [modalities, setModalities] = useState<ModalityListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    modalitiesApi.getAll({
      season_id: loadedSeason?.id
    })
      .then(data => setModalities(data))
      .catch(err => {
        console.error("Failed to fetch modalities:", err);
        notify("Erro ao carregar modalidades.", "error");
      })
      .finally(() => setLoading(false));
  }, [loadedSeason?.id]);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Modalidades ({modalities?.length || 0})</h1>
            <div>
              <Button
                onClick={() => pushModal(
                <ModalityCreateModal
                    onCreate={(newModality) => {
                      navigate(`/modalidades/${newModality.id}`);
                    }}
                  />
                )}
                type='primary'
                active={isAdminGeneral}
              >
                + Adicionar Modalidade
              </Button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            {loading ? (
              <p className="text-gray-500 text-center py-8">Carregando modalidades...</p>
            ) : (
              <ModalitiesListComponent
                modalities={modalities || []}
              />
            )}
          </div>
        </div>
      </div>
  );
};

export default Modalities;
