import { useNavigate } from 'react-router-dom';
import { useKeycloak } from '../auth/KeycloakProvider';
import { useEffect } from 'react';

function Login() {
  const { login, authenticated, hasRole} = useKeycloak();
  const navigate = useNavigate();

  useEffect(() => {
    if (authenticated) {
      if (hasRole('admin_geral')) {
        navigate('/geral/dashboard', { replace: true });
      } else if (hasRole('admin_nucleo')) {
        navigate('/nucleo/dashboard', { replace: true });
      } else {
        navigate('/unauthorized', { replace: true });
      }
    }
  }, [authenticated, navigate, hasRole]);


  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage: 'url("https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=2090")',
      }}
    >
      <div className="absolute inset-0 bg-black bg-opacity-40"></div>

      <div className="relative z-10 bg-white rounded-lg shadow-2xl p-12 w-full max-w-xl mx-auto">
        <h1 className="text-5xl font-bold text-center mb-8 text-gray-800">LOG IN</h1>

        <div className="border-t border-gray-300 mb-8"></div>

        <div className="grid grid-cols-2 gap-6 mb-8">
          <button
            onClick={() => navigate('/login/geral')}
            className="bg-teal-500 hover:bg-teal-600 text-white rounded-lg p-8 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Admin</h2>
              <h3 className="text-2xl font-bold">Geral</h3>
            </div>
          </button>

          <button
            onClick={() => login()}
            className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-teal-200 flex items-center justify-center gap-3"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            Entrar no Sistema
          </button>

          <div className="relative flex items-center py-2">
            <div className="flex-grow border-t border-gray-300"></div>
            <span className="flex-shrink mx-4 text-gray-400 text-xs uppercase">ou</span>
            <div className="flex-grow border-t border-gray-300"></div>
          </div>

        <div className="text-center">
          <a
            href="/"
            className="text-sm text-teal-700 hover:text-teal-900 font-semibold transition-colors"
          >
            Voltar ao site público
          </a>
        </div>
      </div>
    </div>
  );
}

export default Login;
