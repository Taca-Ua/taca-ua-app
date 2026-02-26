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
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>

      <div className="relative z-10 bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl p-10 w-full max-w-md mx-4 text-center">
        <div className="mb-8">
          <h1 className="text-4xl font-black text-teal-600 tracking-tight">TaçaUa</h1>
          <p className="text-gray-500 mt-2 font-medium">Portal de Administração</p>
        </div>

        <div className="space-y-6">
          <p className="text-sm text-gray-600">
            Utilize as suas credenciais para acessar o painel de administração.
          </p>

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
