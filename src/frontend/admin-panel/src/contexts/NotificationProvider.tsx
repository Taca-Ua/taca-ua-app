import { useState, useCallback, useContext } from 'react';
import type { ReactNode } from 'react';
import { NotificationContext } from './NotificationContext';
import type { Notification, NotificationType } from './NotificationContext';
import { NotificationContainer } from '../components/NotificationContainer';

const TTL_DEFAULT_MS = 3_000;
const TTL_ERROR_MS = 6_000;

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const dismiss = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const notify = useCallback((message: string, type: NotificationType = 'info') => {
    const id = `${Date.now()}-${Math.random()}`;
    setNotifications((prev) => [...prev, { id, type, message }]);

    const ttl = type === 'error' ? TTL_ERROR_MS : TTL_DEFAULT_MS;
    setTimeout(() => dismiss(id), ttl);
  }, [dismiss]);

  return (
    <NotificationContext.Provider value={{ notify }}>
      {children}
      <NotificationContainer notifications={notifications} onDismiss={dismiss} />
    </NotificationContext.Provider>
  );
};

/** Hook to access the notification context from any child component. */
export const useNotification = () => {
  const ctx = useContext(NotificationContext);
  if (!ctx) {
    throw new Error('useNotification must be used inside <NotificationProvider>');
  }
  return ctx;
};
