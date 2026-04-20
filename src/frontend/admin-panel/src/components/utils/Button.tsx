import { useState } from "react";
import ConfirmModal from "../ConfirmModal";

const Button = ( {
    onClick,
    type = "primary",
    active = true,
    disabled = false,
    confirmation,
    padding = "px-4 py-3",
    flexible = false,
    children,
} : {
    onClick: () => void;
    type?: "primary" | "danger" | "secondary" | "info" | "success";
    active?: boolean;
    disabled?: boolean;
    confirmation?: {
        title: string;
        message: string;
        confirmLabel: string;
        cancelLabel?: string;
    };
    padding?: string;
    flexible?: boolean;
    children?: React.ReactNode;
} ) => {

    const [showConfirm, setShowConfirm] = useState(false);

    const baseClasses = `${flexible ? "flex-1" : ""} ${padding} rounded-md font-medium transition-colors text-center`;
    const typeClasses = {
        primary: "bg-teal-700 hover:bg-teal-800 text-white disabled:opacity-50 disabled:hover:bg-teal-700",
        secondary: "bg-gray-300 hover:bg-gray-400 text-gray-800 disabled:opacity-50 disabled:hover:bg-gray-200",
        danger: "bg-red-600 hover:bg-red-700 text-white disabled:opacity-50 disabled:hover:bg-red-400",
        info: "bg-blue-700 hover:bg-blue-800 text-white disabled:opacity-50 disabled:hover:bg-blue-400",
        success: "bg-green-700 hover:bg-green-800 text-white disabled:opacity-50 disabled:hover:bg-green-400",
    };

    if ( !active ) return null; // Don't render the button if it's not active

    return (
        <>
        <button
            onClick={() => {
                if (confirmation) {
                    setShowConfirm(true);
                } else {
                    onClick();
                }
            }}
            className={`${baseClasses} ${typeClasses[type]}`}
            disabled={disabled}
        >
            {children}
        </button>
        {confirmation && (
            <ConfirmModal
                isOpen={showConfirm}
                title={confirmation.title}
                message={confirmation.message}
                confirmLabel={confirmation.confirmLabel}
                cancelLabel={confirmation.cancelLabel ? confirmation.cancelLabel : "Cancelar"}
                variant={type === "danger" ? "danger" : "success"}
                onCancel={() => setShowConfirm(false)}
                onConfirm={() => {
                    setShowConfirm(false);
                    onClick();
                }}
            />
        )}
        </>
    );
}

export default Button;
