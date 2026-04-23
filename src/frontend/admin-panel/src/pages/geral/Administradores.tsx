
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { administratorsApi, type AdminListItem } from '../../api/admins';
import { useNotification } from '../../contexts/NotificationProvider';
import AdminCreateModal from '../../components/admins/AdminCreateModal';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';


function Administradores() {
  const navigate = useNavigate();
  const [members, setMembers] = useState<AdminListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const { notify } = useNotification();
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [adminsData] = await Promise.all([
          administratorsApi.getAll(),
        ]);
        setMembers(adminsData);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        notify('Não foi possível carregar a lista de administradores. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredMembers = members.filter(m => {
    const matchesSearch =
      m.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.email.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });
  const AdminG = filteredMembers
    .filter(m => m.role === 'general_admin')
    .sort((a, b) => a.username.localeCompare(b.username));
  const AdminN = filteredMembers
    .filter(m => m.role === 'nucleo_admin')
    .sort((a, b) => a.username.localeCompare(b.username));

  if (loading) {
    return (
      <div className="flex-1 flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">Administradores</h1>
            <div>
              <Button
                onClick={() => pushModal(
                  <AdminCreateModal
                    onCreated={admin => setMembers(prev => [...prev, admin])}
                  />
                )}
                type='primary'
                active={isAdminGeneral} // Only general admins can add new admins
              >
                + Adicionar Administrador
              </Button>
            </div>
          </div>

          <div className="flex gap-3 mb-6">
            <input
              type="text"
              placeholder="Pesquisar administrador..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Administradores Gerais</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {AdminG.map((admin) => (
                <button
                  key={admin.id}
                  type="button"
                  onClick={() => navigate(`/administradores/${admin.id}`)}
                  className="w-full text-left bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{admin.username}</span>
                    <span className="text-gray-600 text-sm">{admin.first_name} {admin.last_name} - {admin.email}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Administradores Núcleo</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {AdminN.map((admin) => (
                <button
                  key={admin.id}
                  type="button"
                  onClick={() => navigate(`/administradores/${admin.id}`)}
                  className="w-full text-left bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{admin.username}</span>
                    <span className="text-gray-600 text-sm">{admin.first_name} {admin.last_name} - {admin.email}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
  );
}

export default Administradores;
