import { useState } from "react";
import { type StaffListItem, staffApi } from "../../api/staff"
import HelpTooltip from "../HelpTooltip";
import DefinedStatesMenuComponent from "../utils/costum_menus/DefinedStatesMenuComponent";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";

const StaffCreateModal = ( {
    onCreate
} : {
    onCreate?: (newStaff: StaffListItem) => void
} ) => {

    const { notify } = useNotification();
    const { popModal } = useModal();

    const [memberName, setMemberName] = useState("");
    const [contact, setContact] = useState("");
    const [staffNumber, setStaffNumber] = useState("");
    const [identifierType, setIdentifierType] = useState<'contact' | 'staff_number'>('contact');

    const onClose = () => {
        popModal();
        setMemberName('');
        setContact('');
        setStaffNumber('');
        setIdentifierType('contact');
    }

    const handleAddMember = () => {
        if (!memberName.trim()) {
            notify('Por favor, preencha o nome.', 'error');
            return;
        }

        const staffData: { full_name: string; contact?: string; staff_number?: string } = {
          full_name: memberName,
        };

        if (identifierType === 'contact') {
          const trimmedContact = contact.trim();

            if (!trimmedContact) {
                notify('Por favor, preencha o contacto.', 'error');
                return;
            }

            if (!/^\+?\d+$/.test(trimmedContact)) {
                notify('O contacto (telemóvel) deve conter apenas dígitos e pode ter um "+" no início.', 'error');
                return;
            }

            if (trimmedContact.length > 13) {
                notify('O contacto (telemóvel) não pode ter mais de 13 caracteres.', 'error');
                return;
            }

            staffData.contact = trimmedContact;
        } else {
            const trimmedStaffNumber = staffNumber.trim();

            if (!trimmedStaffNumber) {
                notify('Por favor, preencha o número de staff.', 'error');
                return;
            }

            if (!/^\d+$/.test(trimmedStaffNumber)) {
                notify('O número de staff deve conter apenas dígitos.', 'error');
                return;
            }

            if (trimmedStaffNumber.length > 13) {
                notify('O número de staff não pode ter mais de 13 caracteres.', 'error');
                return;
            }

            staffData.staff_number = trimmedStaffNumber;
        }

        staffApi.create(staffData).then((newStaff) => {
            if (onCreate) onCreate(newStaff);
            notify('Membro adicionado com sucesso!', 'success');
        }).catch((err) => {
            console.error("Failed to create staff member:", err);
            notify('Erro ao adicionar membro. Tente novamente.', 'error');
        }).finally(() => {
            onClose();
        });

    }

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Adicionar Membro
          </h2>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="memberName"
                className="block text-gray-700 font-medium mb-2"
              >
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="memberName"
                value={memberName}
                onChange={(e) => setMemberName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Digite o nome do membro"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">
                Identificação{" "}
                <HelpTooltip
                  text="Escolha como identificar o colaborador: por contacto telefónico ou número de staff. Pelo menos um é obrigatório para o registo."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <DefinedStatesMenuComponent
                states={[
                  { value: "contact", label: "Contacto" },
                  { value: "staff_number", label: "Nº Staff" },
                ]}
                onSelect={(value) =>
                  setIdentifierType(value as "contact" | "staff_number")
                }
                initialValue={identifierType}
              />

              {identifierType === "contact" ? (
                <input
                  type="tel"
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o contacto (ex: 912345678)"
                />
              ) : (
                <input
                  type="text"
                  value={staffNumber}
                  onChange={(e) => setStaffNumber(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o número de staff"
                />
              )}
            </div>
          </div>

          <div className="flex gap-4 mt-6">
            <Button onClick={onClose} type="secondary" flexible={true}>
              Cancelar
            </Button>
            <Button onClick={handleAddMember} type="primary" flexible={true}>
              Adicionar
            </Button>
          </div>
        </div>
    );
}

export default StaffCreateModal;
