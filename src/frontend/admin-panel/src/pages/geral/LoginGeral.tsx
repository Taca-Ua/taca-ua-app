import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

function LoginGeral() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(username, password);

      // Verify the user has geral role
      const storedUser = localStorage.getItem('auth_user');
      if (storedUser) {
        const user = JSON.parse(storedUser);
        if (user.role === 'geral') {
          navigate('/geral/dashboard');
        } else {
          setError('Acesso negado. Esta conta não é de administrador geral.');
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }
    } catch (err) {
      setError('Credenciais inválidas. Por favor, tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage: 'url("https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=2090")',
      }}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-40"></div>

      {/* Login Card */}
      <div className="relative z-10 bg-white rounded-lg shadow-2xl p-12 w-full max-w-md mx-auto">
        <h1 className="text-5xl font-bold text-center mb-2 text-gray-800">LOG IN</h1>
        <h2 className="text-2xl font-semibold text-center mb-8 text-teal-500">Administrador Geral</h2>

        <div className="border-t border-gray-300 mb-8"></div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-center text-teal-500 font-semibold mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={isLoading}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-teal-500 transition-colors bg-gray-100 disabled:opacity-50"
              placeholder=""
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-center text-teal-500 font-semibold mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-teal-500 transition-colors bg-gray-100 disabled:opacity-50"
              placeholder=""
            />
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 rounded-lg transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'A entrar...' : 'Entrar'}
            </button>
          </div>
        </form>

        <div className="border-t border-gray-300 mt-8 mb-6"></div>

        {/* Back button */}
        <div className="text-center">
          <button
            onClick={() => navigate('/login')}
            className="inline-block bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-md transition-colors"
          >
            Voltar à Seleção
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginGeral;
