import Button from "./utils/Button";

type ConfirmModalProps = {
  isOpen: boolean;
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
  isOpen,
  title,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  variant = 'primary',
  loading = false,
  onConfirm,
  onCancel
}: ConfirmModalProps) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={() => {
        if (!loading) {
          onCancel();
        }
      }}
    >
      <div
        className="bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-lg"
        onClick={(e: any) => e.stopPropagation()}
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
    </div>
  );
};

export default ConfirmModal;
