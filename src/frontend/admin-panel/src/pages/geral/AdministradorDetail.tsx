
import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { administratorsApi, type AdminDetail } from '../../api/admins';
import { useNotification } from '../../contexts/NotificationProvider';
import AdminInfoComponent from '../../components/admins/AdminInfoComponent';
import Button from '../../components/utils/Button';

function AdminDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [member, setMember] = useState<AdminDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();


  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const adminData = await administratorsApi.getById(String(id));
        setMember(adminData);
      } catch (err) {
        console.error('Failed to fetch administrator:', err);
        notify('Não foi possível carregar os dados do administrador. Tente recarregar a página.', 'error');
        navigate('/geral/administradores');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex-1 flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (!member) return null;

  return (
      <div className="flex-1 p-8 max-w-3xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes do Administrador</h1>
          <div>
            <Button
              onClick={() => navigate(`/geral/administradores/`)}
              type='secondary'
              padding='px-6 py-3'
            >
              Voltar
            </Button>
          </div>
        </div>

        <AdminInfoComponent
          adminState={[member, setMember]}
        />
      </div>
  );
}

export default AdminDetailPage;
