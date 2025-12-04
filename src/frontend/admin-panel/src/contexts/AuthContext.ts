import { createContext } from 'react';

export interface User {
  id: number;
  username: string;
  email: string;
  course_id: number;
  course_abbreviation: string;
  full_name: string;
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
