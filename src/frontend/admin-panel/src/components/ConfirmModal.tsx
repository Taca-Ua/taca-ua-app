import Button from "./utils/Button";
import React, { useRef, useEffect } from "react";

type ConfirmModalProps = {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'primary' | 'success';
  loading?: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
};


const ConfirmModal = ({
  title,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  variant = 'primary',
  loading = false,
  onConfirm,
  onCancel
}: ConfirmModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle Enter key to trigger confirm
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' && !loading) {
      onConfirm();
    }
  };

  useEffect(() => {
    if (modalRef.current) {
      modalRef.current.focus();
    }
  }, []);

  return (
    <div
      ref={modalRef}
      className="bg-white rounded-lg p-8 w-full max-w-md shadow-lg"
      onClick={(e: any) => e.stopPropagation()}
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      <h2 className="text-2xl font-bold mb-4 text-gray-800">{title}</h2>
      <p className="text-gray-600 mb-6">{message}</p>

      <div className="flex gap-4">
        <Button
          onClick={onCancel}
          type="secondary"
          active={!loading}
          flexible={true}
        >
          {cancelLabel}
        </Button>
        <Button
          onClick={onConfirm}
          type={variant}
          active={!loading}
          flexible={true}
        >
          {loading ? 'A processar...' : confirmLabel}
        </Button>
      </div>
    </div>
  );
};

export default ConfirmModal;
