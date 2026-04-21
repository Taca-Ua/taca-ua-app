import { useEffect, useState } from "react";
import { modalityTypesApi, type ModalityTypeDetail, type ModalityTypeListItem } from "../../api/modality-types";
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';
import ModalityTypeCreateModal from "../../components/modality-types/ModalityTypeCreateModal";
import ModalityTypeInfoModal from "../../components/modality-types/ModalityTypeInfoModal";
import Button from "../../components/utils/Button";

const ModalityTypes = () => {
  const [scoringFormats, setModalityTypes] = useState<ModalityTypeListItem[]>([]);
  const [loading] = useState(false);
  const { notify } = useNotification();

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ModalityTypeListItem | null>(null);
  const [loadedFormatDetails, setLoadedFormatDetails] = useState<ModalityTypeDetail | null>(null);

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const formats = await modalityTypesApi.getAll();
        if (!mounted) return;
        setModalityTypes(formats);
      } catch (err) {
        console.error('Failed to fetch scoring formats:', err);
        if (!mounted) return;
        notify('Não foi possível carregar os formatos de prova. Tente recarregar a página.', 'error');
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!isViewModalOpen || !selectedFormat) {
      setLoadedFormatDetails(null);
      return;
    }

    // Load full details for the selected format
    modalityTypesApi.getById(selectedFormat.id).then(formatDetails => {
      setLoadedFormatDetails(formatDetails);
    }).catch(err => {
      console.error('Failed to load format details:', err);
      notify('Não foi possível carregar os detalhes do formato de prova. Tente novamente.', 'error');
      setIsViewModalOpen(false);
    });

  }, [isViewModalOpen, selectedFormat]);

  const handleViewFormat = (format: ModalityTypeListItem) => {
    setSelectedFormat(format);
    setIsViewModalOpen(true);
  };

  return (
      <div className="flex-1 p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Formatos de Prova</h1>

          <Button
            onClick={() => setIsCreateModalOpen(true)}
            type="primary"
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
          ) : scoringFormats.length > 0 ? (
            [...scoringFormats].sort((a, b) => a.name.localeCompare(b.name)).map(format => (
              <button
                key={format.id}
                type="button"
                className="w-full text-left p-4 bg-gray-100 rounded-md hover:bg-gray-200 flex justify-between items-center transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                onClick={() => handleViewFormat(format)}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-lg">{format.name}</span>
                    {format.is_playoff && (
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-semibold rounded-full border border-amber-300">
                        Playoff
                      </span>
                    )}
                    {!format.is_playoff && format.tournament_competitor_type && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${format.tournament_competitor_type === 'individual' ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-green-100 text-green-700 border-green-300'}`}>
                        {format.tournament_competitor_type === 'individual' ? 'Individual' : 'Equipa'}
                      </span>
                    )}
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

        <ModalityTypeCreateModal
          controller={[isCreateModalOpen, setIsCreateModalOpen]}
          onCreate={newFormat => setModalityTypes((prev) => [...prev, newFormat])}
        />

        {loadedFormatDetails && (
          <ModalityTypeInfoModal
            controller={[isViewModalOpen, setIsViewModalOpen]}
            modalityTypeState={[loadedFormatDetails, setLoadedFormatDetails]}
          />
        )}
      </div>
  );
};

export default ModalityTypes;
