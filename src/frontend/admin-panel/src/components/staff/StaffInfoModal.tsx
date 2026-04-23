import { useModal } from "../../contexts/ModalContext";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";
import { staffApi, type StaffDetail } from "../../api/staff";
import { useEffect, useState } from "react";
import StaffEditModal from "./StaffEditModal";

const StaffInfoModal = ( {
    staffId,
    onEditSave,
    onDelete,
} : {
    staffId: string,
    onEditSave?: (updated: any) => void,
    onDelete?: () => void,
} ) => {
    const { popModal, pushModal } = useModal();
    const { notify } = useNotification();

    const [staff, setStaff] = useState<StaffDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        setIsLoading(true);
        staffApi.getById(staffId)
        .then((data) => {
            setStaff(data);
            setIsLoading(false);
        })
        .catch((err) => {
            console.error('Failed to fetch staff details:', err);
            notify("Failed to load staff details.", "error");
            setIsLoading(false);
            onClose();
        });
    }, [staffId]);

    const onClose = () => {
        popModal();
    }

    const handleDelete = () => {
        staffApi.delete(staffId)
        .then(() => {
            if (onDelete) onDelete();
            popModal();
        })
        .catch((err) => {
            console.error('Failed to delete staff:', err);
            notify("Failed to delete staff.", "error");
        });
    }

    if (isLoading) {
        return (
            <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
                <p className="text-gray-500 text-center">Carregando detalhes do staff...</p>
            </div>
        );
    }

    if (!staff) return null;

    return (
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <span className="inline-block px-4 py-2 rounded-full text-sm font-medium bg-purple-100 text-purple-700">
                Staff
              </span>
              <h2 className="text-2xl font-bold text-gray-800">
                {staff.full_name}
              </h2>
            </div>

            <div>
              {
                staff.staff_number ? (
                  <>
                    <label className="block text-teal-500 font-medium mb-2">
                        Número de Staff
                    </label>
                    <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                        {staff.staff_number}
                    </div>
                  </>
                ) : staff.contact ? (
                  <>
                    <label className="block text-teal-500 font-medium mb-2">
                        Contacto
                    </label>
                    <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                        {staff.contact}
                    </div>
                  </>
                ) : null
              }
            </div>
          </div>

          <div className="flex gap-4 mt-4">
            <Button onClick={onClose} type="secondary" flexible={true}>
              Fechar
            </Button>
            <Button
              onClick={() => pushModal(
                <StaffEditModal
                  staffState={[staff, setStaff]}
                  onSave={(updated) => {
                    if (onEditSave) onEditSave(updated);
                  }}
                />
              )}
              type="primary"
              flexible={true}
            >
              Editar
            </Button>
            <Button
              onClick={handleDelete}
              type="danger"
              flexible={true}
              confirmation={{
                title: "Tem certeza que deseja eliminar este staff?",
                message: "Esta ação é irreversível.",
                confirmLabel: "Sim, eliminar",
              }}
            >
              Eliminar
            </Button>
          </div>
        </div>
    );
}

export default StaffInfoModal;
