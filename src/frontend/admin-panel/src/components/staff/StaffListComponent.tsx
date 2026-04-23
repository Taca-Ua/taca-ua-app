import { useState } from "react";
import { type StaffListItem } from "../../api/staff"
import { useModal } from "../../contexts/ModalContext";
import StaffInfoModal from "./StaffInfoModal";

const StaffListBanner = ({ staff, onDelete }: { staff: StaffListItem; onDelete?: () => void }) => {
    const { pushModal } = useModal();

    const [staffState, setStaffState] = useState(staff);

    return (
      <li
        key={staffState.id}
        className="px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:bg-gray-50"
      >
        <div className="min-w-0 flex-1" onClick={() => pushModal(
          <StaffInfoModal
            staffId={staff.id}
            onEditSave={(updated) => {
              setStaffState(updated);
            }}
            onDelete={() => {
              if (onDelete) onDelete();
            }}
          />
        )}>
          <p className="font-medium text-teal-700">{staffState.full_name}</p>

          <div className="text-sm text-gray-600 mt-0.5">
            {staffState.staff_number
              ? `Número de Staff: ${staffState.staff_number}`
              : `Contato: ${staffState.contact || "N/A"}`}
          </div>
        </div>
      </li>
    );
}

const StaffListComponent = ( {
    staffListState,
} : {
    staffListState: [StaffListItem[] | null, React.Dispatch<React.SetStateAction<StaffListItem[] | null>>],
} ) => {

    const [staffList, setStaffList] = staffListState;

    if (staffList === null) {
        return (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 animate-spin text-gray-400"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p className="mt-2 text-sm text-gray-500">Carregando staff...</p>
          </div>
        );
    }

    if (staffList.length === 0) {
        return (
          <div className="text-center py-12 text-gray-500">
            Nenhum membro de staff corresponde aos filtros.
          </div>
        );
    }

    return (
      <ul className="divide-y divide-gray-100 max-h-[640px] overflow-y-auto">
        {staffList
          .sort((a, b) => a.full_name.localeCompare(b.full_name))
          .map((staff) => (
            <StaffListBanner key={staff.id} staff={staff} onDelete={() => {
              setStaffList((prev) => prev ? prev.filter((s) => s.id !== staff.id) : null);
            }}/>
          ))}
      </ul>
    );
}

export default StaffListComponent;
