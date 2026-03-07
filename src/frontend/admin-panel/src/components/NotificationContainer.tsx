import type { Notification } from '../contexts/NotificationContext';

interface NotificationContainerProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
}

const TYPE_STYLES: Record<Notification['type'], string> = {
  success: 'bg-green-600 border-green-400',
  error:   'bg-red-700   border-red-500',
  info:    'bg-blue-600  border-blue-400',
  warning: 'bg-yellow-500 border-yellow-300 text-gray-900',
};

const TYPE_ICON: Record<Notification['type'], string> = {
  success: '✓',
  error:   '✕',
  info:    'ℹ',
  warning: '⚠',
};

export const NotificationContainer = ({ notifications, onDismiss }: NotificationContainerProps) => {
  if (notifications.length === 0) return null;

  return (
    <div
      aria-live="polite"
      aria-label="Notifications"
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80 pointer-events-none"
    >
      {notifications.map((n) => (
        <div
          key={n.id}
          role="alert"
          className={`
            flex items-start gap-3 rounded-lg border px-4 py-3 text-sm text-white shadow-lg
            pointer-events-auto
            animate-slideIn
            ${TYPE_STYLES[n.type]}
          `}
        >
          <span className="mt-0.5 shrink-0 font-bold">{TYPE_ICON[n.type]}</span>
          <span className="flex-1 break-words">{n.message}</span>
          <button
            onClick={() => onDismiss(n.id)}
            aria-label="Dismiss notification"
            className="shrink-0 opacity-70 hover:opacity-100 transition-opacity ml-1 leading-none"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};
