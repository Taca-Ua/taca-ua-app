import { createBrowserRouter } from 'react-router-dom';
import DashboardNucleo from '../pages/nucleo/DashboardNucleo';
import Membros from '../pages/nucleo/Membros';
import MemberDetail from '../pages/nucleo/MemberDetail';
import NotFound from '../pages/NotFound';
import Login from '../pages/Login';
import LoginGeral from '../pages/geral/LoginGeral';
import LoginNucleo from '../pages/nucleo/LoginNucleo';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Login />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/login/geral',
    element: <LoginGeral />,
  },
  {
    path: '/login/nucleo',
    element: <LoginNucleo />,
  },
  {
    path: '/nucleo/dashboard',
    element: <DashboardNucleo />,
  },
  {
    path: '/nucleo/membros',
    element: <Membros />,
  },
  {
    path: '/nucleo/membros/:id',
    element: <MemberDetail />,
  },
  {
    path: '/dashboard',
    element: <DashboardNucleo />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
], {
  basename: '/admin'
});
