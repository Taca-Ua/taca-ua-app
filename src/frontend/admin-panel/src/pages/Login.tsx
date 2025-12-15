import { useNavigate } from 'react-router-dom';
import { useKeycloak } from '../auth/KeycloakProvider';
import { useEffect } from 'react'; // <-- ¡Importar useEffect!

/**
 * Login Component: Initiates the Keycloak authentication flow
 * and handles post-login redirection based on user roles.
 */
function Login() {
  const { login, authenticated, hasRole } = useKeycloak();
  const navigate = useNavigate();



  useEffect(() => {
    if (authenticated) {

      if (hasRole('admin_geral')) {
        navigate('/geral/dashboard', { replace: true });
        return;
      }

      if (hasRole('admin_nucleo')) { // <-- Asumiendo este es el nombre
        navigate('/nucleo/dashboard', { replace: true });
        return;
      }

      navigate('/unauthorized', { replace: true }); // <-- Usar la ruta completa
    }
  }, [authenticated, navigate, hasRole]);

  const handleAdminLogin = () => {
    login();
  };

  if (authenticated) {
      return null;
  }


  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage: 'url("https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=2090")',
      }}
    >
      {/* Overlay to darken the background image */}
      <div className="absolute inset-0 bg-black bg-opacity-40"></div>

      {/* Login Card Container */}
      <div className="relative z-10 bg-white rounded-lg shadow-2xl p-12 w-full max-w-xl mx-auto">
        <h1 className="text-5xl font-bold text-center mb-8 text-gray-800">LOGIN</h1>

        <div className="border-t border-gray-300 mb-8"></div>

        {/* Admin Login Options: Both buttons trigger handleAdminLogin */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* Admin Geral Button */}
          <button
            onClick={handleAdminLogin} // Triggers Keycloak redirect
            className="bg-teal-500 hover:bg-teal-600 text-white rounded-lg p-8 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Admin</h2>
              <h3 className="text-2xl font-bold">Geral</h3>
            </div>
          </button>

          {/* Admin Núcleo Button */}
          <button
            onClick={handleAdminLogin} // Triggers Keycloak redirect
            className="bg-teal-500 hover:bg-teal-600 text-white rounded-lg p-8 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Admin</h2>
              <h3 className="text-2xl font-bold">Núcleo</h3>
            </div>
          </button>
        </div>

        <div className="border-t border-gray-300 mb-6"></div>

        {/* Back to main site link */}
        <div className="text-center">
          <a
            href="/"
            className="inline-block bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-md transition-colors"
          >
            Voltar à Página Principal
          </a>
        </div>
      </div>
    </div>
  );
}

export default Login;
