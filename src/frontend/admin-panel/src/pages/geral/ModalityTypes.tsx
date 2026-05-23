import { useEffect, useState } from "react";
import { modalityTypesApi, type ModalityTypeListItem } from "../../api/modality-types";
import { useNotification } from '../../contexts/NotificationProvider';
import ModalityTypeCreateModal from "../../components/modality-types/ModalityTypeCreateModal";
import ModalityTypeInfoModal from "../../components/modality-types/ModalityTypeInfoModal";
import Button from "../../components/utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";
import { useSeason } from "../../contexts/SeasonContext";
import SeasonSelector from "../../components/seasons/SeasonSelector";
import { ModalityTypeBadge } from "../../components/modality-types/utils";

const ModalityTypes = () => {
  const { notify } = useNotification();
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();
  const { loadedSeason } = useSeason();

  const [modalityTypes, setModalityTypes] = useState<ModalityTypeListItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    modalityTypesApi.getAll({
      season_id: loadedSeason?.id
    })
      .then((formats) => setModalityTypes(formats))
      .catch((err) => {
        console.error('Failed to fetch modality types:', err);
        notify('Não foi possível carregar os formatos de prova. Tente recarregar a página.', 'error');
        setModalityTypes([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [loadedSeason?.id]);

  const sortedModalityTypes = modalityTypes.sort((a, b) => a.name.localeCompare(b.name));

  return (
    <>
      <SeasonSelector />
      <div className="flex-1 p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Formatos de Prova</h1>

          <Button
            onClick={() => pushModal(
              <ModalityTypeCreateModal
                onCreate={newFormat => setModalityTypes((prev) => [...prev, newFormat])}
              />
            )}
            type="primary"
            active={isAdminGeneral}
          >
            + Adicionar Formato
          </Button>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : modalityTypes.length > 0 ? (
            sortedModalityTypes.map(format => (
              <button
                key={format.id}
                type="button"
                className="w-full text-left p-4 bg-gray-100 rounded-md hover:bg-gray-200 flex justify-between items-center transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                onClick={() => pushModal(
                  <ModalityTypeInfoModal
                    modalityTypeId={format.id}
                    onDelete={() => setModalityTypes((prev) => prev.filter((f) => f.id !== format.id))}
                    onEdit={(updatedFormat) => setModalityTypes((prev) => prev.map((f) => f.id === updatedFormat.id ? updatedFormat : f))}
                  />
                )}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-lg">{format.name}</span>
                    <ModalityTypeBadge format={format} />
                  </div>
                  {format.description && (
                    <div className="text-sm text-gray-600 mt-1">{format.description}</div>
                  )}
                  <div className="text-sm text-gray-500 mt-1">
                    {format.num_escaloes} {format.num_escaloes !== 1 ? 'escalões' : 'escalão'}
                  </div>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">Nenhum formato de prova encontrado.</p>
          )}
        </div>
      </div>
    </>
  );
};

export default ModalityTypes;
