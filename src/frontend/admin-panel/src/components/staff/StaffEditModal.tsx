import { useModal } from "../../contexts/ModalContext";
import { staffApi, type StaffDetail } from "../../api/staff";
import Button from "../utils/Button";
import { useState } from "react";
import { useNotification } from "../../contexts/NotificationProvider";

const StaffEditModal = ( {
    staffState,
    onSave,
} : {
    staffState: [StaffDetail, React.Dispatch<React.SetStateAction<StaffDetail | null>>],
    onSave?: (updated: StaffDetail) => void,
} ) => {

    const { popModal } = useModal();
    const { notify } = useNotification();

    const [staff, setStaff] = staffState;
    const [editedName, setEditedName] = useState(staff.full_name);

    const onClose = () => {
        popModal();
    }

    const handleSave = () => {
        if (editedName.trim() === "") {
            notify("O nome do membro não pode estar vazio.", "error");
            return;
        }

        staffApi.update(staff.id, { full_name: editedName })
            .then((updatedStaff) => {
                setStaff(updatedStaff);
                if (onSave) onSave(updatedStaff);
                popModal();
            })
            .catch((err) => {
                console.error("Failed to update staff member:", err);
                notify("Falha ao atualizar o membro.", "error");
            });
    }

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Editar Membro
          </h2>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="editName"
                className="block text-gray-700 font-medium mb-2"
              >
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="editName"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o nome do membro"
              />
            </div>
          </div>

          <div className="flex gap-4 mt-6">
            <Button
                onClick={onClose}
                type="secondary"
                flexible={true}
            >
                Cancelar
            </Button>
            <Button
              onClick={handleSave}
              type="primary"
              flexible={true}
            >
              Guardar
            </Button>
          </div>
        </div>
    );
}

export default StaffEditModal;
