import { type ModalityTypeDetail, modalityTypesApi } from "../../api/modality-types";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";
import ModalityTypeEditModal from "./ModalityTypeEditModal";
import { useModal } from "../../contexts/ModalContext";
import { useEffect, useState } from "react";
import { useAuth } from "../../hooks/useAuth";

const ModalityTypeInfoModal = ( {
    modalityTypeId,
    onDelete
} : {
    modalityTypeId: string;
    onDelete?: () => void;
} ) => {
    const { notify } = useNotification();
    const { popModal, pushModal } = useModal();
    const { isAdminGeneral } = useAuth();

    const [modalityType, setModalityType] = useState<ModalityTypeDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
      setIsLoading(true);
      modalityTypesApi.getById(modalityTypeId).then(format => {
        setModalityType(format);
      }).catch(err => {
        console.error("Failed to load modality type details:", err);
        notify("Não foi possível carregar os detalhes do formato de prova. Tente novamente.", "error");
        popModal();
      }).finally(() => {
        setIsLoading(false);
      });
    }, [modalityTypeId]);

    const getParticipantsText = (min: number | null, max: number | null) => {
        if (max === null && min === null) return '—';
        if (max === null) return `mais de ${min}`;
        if (min === null) return `até ${max}`;
        if (min === max) return `${min}`;
        return `${min} a ${max}`;
    };

    const handleDeleteFormat = () => {
      if (!modalityType) return;
        modalityTypesApi.delete(modalityType.id).then(() => {
            notify("Formato eliminado com sucesso!", "success");
            if (onDelete) onDelete();
        }).catch((err) => {
            console.error("Erro ao eliminar formato:", err);
            notify("Não foi possível eliminar o formato. Tente novamente.", "error");
        }).finally(() => {
            popModal();
        });
    };

    if (isLoading) {
      return (
        <div className="bg-white p-8 rounded-lg w-full max-w-5xl my-8">
          <p className="text-gray-500">Carregando detalhes do formato de prova...</p>
        </div>
      );
    }

    if (!modalityType) return null; // Could show a loading state here if desired

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-max md:min-w-[500px]">
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold">{modalityType.name}</h2>
            <button
              onClick={() => popModal()}
              className="text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400 rounded"
            >
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="mb-4 flex items-center gap-2">
            {modalityType.is_playoff ? (
              <span className="px-3 py-1 bg-amber-100 text-amber-700 text-sm font-semibold rounded-full border border-amber-300">
                Formato Playoff
              </span>
            ) : (
              <>
                <span className="px-3 py-1 bg-gray-100 text-gray-500 text-sm rounded-full border border-gray-200">
                  Formato Regular
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold border ${modalityType.tournament_competitor_type === "individual" ? "bg-blue-100 text-blue-700 border-blue-300" : "bg-green-100 text-green-700 border-green-300"}`}
                >
                  {modalityType.tournament_competitor_type === "individual"
                    ? "Individual"
                    : "Equipa"}
                </span>
              </>
            )}
          </div>

          {modalityType.description && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Descrição
              </label>
              <p className="text-gray-900">{modalityType.description}</p>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Tabela de Prova</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      Escalão
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      Participantes
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      1º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      2º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      3º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      4º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      5º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      6º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      7º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      8º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      9º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      10º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      11º
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left">
                      12º
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {modalityType.escaloes.map((esc, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 font-medium">
                        {esc.escalao}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {getParticipantsText(
                          esc.minParticipants,
                          esc.maxParticipants,
                        )}
                      </td>
                      {[...Array(12)].map((_, i) => (
                        <td
                          key={i}
                          className="border border-gray-300 px-4 py-2 text-center"
                        >
                          {esc.points[i] ?? "—"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex gap-4 pt-4 border-t">
            <Button
              onClick={handleDeleteFormat}
              type="danger"
              confirmation={{
                title: "Confirmar eliminação",
                message: "Tem a certeza que deseja eliminar este formato? Esta ação não pode ser desfeita.",
                confirmLabel: "Sim, eliminar",
                cancelLabel: "Cancelar"
              }}
              flexible={true}
              active={isAdminGeneral}
            >
                Eliminar
            </Button>
            <Button
                onClick={() => pushModal(<ModalityTypeEditModal modalityTypeState={[modalityType, setModalityType]} />)}
                type="info"
                flexible={true}
                active={isAdminGeneral}
            >
                Editar
            </Button>
            <Button
                onClick={() => popModal()}
                type="secondary"
                flexible={true}
            >
                Fechar
            </Button>
          </div>
        </div>
    );
};

export default ModalityTypeInfoModal;
