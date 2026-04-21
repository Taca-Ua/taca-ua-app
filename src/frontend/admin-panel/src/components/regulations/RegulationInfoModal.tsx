import { useState } from "react";
import { type RegulationDetail, regulationsApi } from "../../api/regulations";
import { useNotification } from "../../contexts/NotificationProvider";
import { btn } from "../../styles/buttonStyles";
import Button from "../utils/Button";
import RegulationEditModal from "./RegulationEditModal";

const formatDisplayDate = (dateStr: string | undefined) => {
    if (!dateStr) return "Data indisponível";

    const date = new Date(dateStr);

    if (isNaN(date.getTime())) {
        const fallbackDate = new Date(dateStr.split('.')[0] + 'Z');
        if (isNaN(fallbackDate.getTime())) return "Data indisponível";
        return fallbackDate.toLocaleDateString('pt-PT', { day: '2-digit', month: 'long', year: 'numeric' });
    }

    return date.toLocaleDateString('pt-PT', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
};


const RegulationInfoModal = ( {
    controller,
    regulationState
} : {
    controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>]
    regulationState: [RegulationDetail | null, React.Dispatch<React.SetStateAction<RegulationDetail | null>>]
} ) => {

    const [ isOpen, setIsOpen ] = controller;
    const { notify } = useNotification();

    const [ regulation, setRegulation ] = regulationState;
    const [ editModalOpen, setEditModalOpen ] = useState(false);

    const onClose = () => {
        setIsOpen(false);
        setRegulation(null);
    };

    const handleDelete = () => {
        if ( !regulation ) return;

        regulationsApi.delete(regulation.id).then(() => {
            onClose();
            notify('Regulation deleted successfully.', 'success');
        }).catch((err: unknown) => {
            console.error('Failed to delete regulation:', err);
            notify('Failed to delete regulation.', 'error');
        });
    }

    if ( !isOpen ) return null;
    if ( !regulation ) return null;

    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
          <div className="p-8">
            <div className="flex justify-between items-start">
              <h2 className="text-2xl font-bold text-gray-900">
                {regulation.title}
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mt-8 space-y-6">
              <div className="grid grid-cols-2 gap-8">
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">
                    Data de Submissão
                  </label>
                  <p className="mt-1 text-gray-900 font-medium">
                    {formatDisplayDate(regulation.created_at)}
                  </p>
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">
                    Tipo de Ficheiro
                  </label>
                  <p className="mt-1 text-gray-900 font-medium">
                    Documento PDF
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest">
                  Descrição
                </label>
                <p className="mt-2 text-gray-700 bg-gray-50 p-4 rounded-lg italic border-l-4 border-gray-200">
                  {regulation.description ||
                    "Nenhuma descrição adicional para este documento."}
                </p>
              </div>

              <div className="p-4 bg-blue-50 rounded-xl flex items-center justify-between border border-blue-100">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-500 p-2 rounded-lg text-white">
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-blue-900">
                      Aceder ao Ficheiro
                    </p>
                    <p className="text-xs text-blue-700">
                      O documento será aberto num novo separador.
                    </p>
                  </div>
                </div>
                <a
                  href={regulation.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`px-4 py-2 ${btn.infoStrong} text-sm font-bold rounded-lg shadow-sm`}
                >
                  Visualizar
                </a>
              </div>
            </div>

            <div className="mt-10 pt-6 border-t border-gray-100 flex gap-4">
              <Button
                onClick={handleDelete}
                type="danger"
                confirmation={{
                  title: "Eliminar regulamento",
                  message: `Tem certeza que deseja eliminar "${regulation.title}"? Esta ação não pode ser desfeita.`,
                  confirmLabel: "Eliminar",
                }}
                flexible={true}
              >
                Eliminar Documento
              </Button>
              <Button onClick={() => setEditModalOpen(true)} type="info" flexible={true}>
                Editar Documento
              </Button>
              <Button onClick={onClose} type="secondary" flexible={true}>
                Fechar
              </Button>
            </div>
          </div>
        </div>

        <RegulationEditModal
            controller={[editModalOpen, setEditModalOpen]}
            regulation={regulation}
            onUpdate={(updatedReg) => setRegulation(updatedReg)}
        />
      </div>
    );
}

export default RegulationInfoModal;
