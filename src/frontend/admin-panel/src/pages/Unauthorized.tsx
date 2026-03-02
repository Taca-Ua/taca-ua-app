import { useAuth } from '../hooks/useAuth';

/**
 * Shown when a successfully-authenticated user does not hold any of the
 * recognised admin roles (general_admin or nucleo_admin).
 */
function Unauthorized() {
  const { logout, username } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white rounded-2xl shadow-lg p-12 max-w-md w-full text-center">
        {/* Icon */}
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-100">
          <svg
            className="h-10 w-10 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
            />
          </svg>
        </div>

        <h1 className="text-2xl font-bold text-gray-800 mb-2">Acesso Negado</h1>

        <p className="text-gray-500 mb-1">
          {username ? (
            <>
              O utilizador{' '}
              <span className="font-semibold text-gray-700">"{username}"</span>{' '}
              não possui permissões de administrador.
            </>
          ) : (
            'A sua conta não possui permissões de administrador.'
          )}
        </p>

        <p className="text-sm text-gray-400 mb-8">
          São necessárias as funções{' '}
          <code className="bg-gray-100 px-1 rounded">general_admin</code> ou{' '}
          <code className="bg-gray-100 px-1 rounded">nucleo_admin</code> no
          Keycloak.
        </p>

        <button
          onClick={logout}
          className="w-full bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
        >
          Terminar Sessão
        </button>
      </div>
    </div>
  );
}

export default Unauthorized;
