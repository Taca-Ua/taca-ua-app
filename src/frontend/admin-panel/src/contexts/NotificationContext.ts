import { createContext } from 'react';

export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
}

export interface NotificationContextType {
  /** Push a new notification. TTL defaults to 3 s (6 s for errors). */
  notify: (message: string, type?: NotificationType) => void;
}

export const NotificationContext = createContext<NotificationContextType | undefined>(undefined);
