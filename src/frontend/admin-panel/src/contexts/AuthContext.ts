import { createContext } from 'react';

export interface User {
  id: number;
  username: string;
  email: string;
  course_id: number | null;
  course_abbreviation: string | null;
  full_name: string;
  role: 'nucleo' | 'geral';
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
