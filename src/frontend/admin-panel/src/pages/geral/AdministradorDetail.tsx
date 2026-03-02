import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from '../../components/geral_navbar';
import { administratorsApi, type AdminDetails } from '../../api/administrators';
import { nucleosApi, type Nucleo } from '../../api/nucleos';

function AdminDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [member, setMember] = useState<AdminDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [editedUserName, setEditedUserName] = useState('');
  const [editedFirstName, setEditedFirstName] = useState('');
  const [editedLastName, setEditedLastName] = useState('');
  const [editedEmail, setEditedEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [editedEnabled, setEditedEnabled] = useState(true);
  const [allNucleos, setAllNucleos] = useState<Nucleo[]>([]);
  const [editedNucleos, setEditedNucleos] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const adminData = await administratorsApi.getById(String(id));
        setMember(adminData);
        setError('');
      } catch (err) {
        console.error('Failed to fetch administrator:', err);
        setError('Erro ao carregar administrador');
        navigate('/geral/administradores');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id, navigate]);

  const handleEdit = () => {
    if (!member) return;
    setEditedUserName(member.username);
    setEditedFirstName(member.first_name);
    setEditedLastName(member.last_name);
    setEditedEmail(member.email);
    setEditedEnabled(member.enabled);
    setEditedNucleos(member.nucleos.map(n => n.id));
    setError('');
    // Fetch all nucleos for the selector
    nucleosApi.getAll().then(setAllNucleos).catch(console.error);
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!member) return;
    if (!editedEmail.trim()) {
      setError('Email é obrigatório');
      return;
    }
    if (!editedFirstName.trim()) {
      setError('Primeiro nome é obrigatório');
      return;
    }
    if (!editedLastName.trim()) {
      setError('Último nome é obrigatório');
      return;
    }

    try {
      await administratorsApi.update(String(id), {
        email: editedEmail,
        first_name: editedFirstName,
        last_name: editedLastName,
        enabled: editedEnabled,
        nucleos: member.role === 'nucleo_admin' ? editedNucleos : undefined,
      });
      // Re-fetch to get updated nucleos
      const refreshed = await administratorsApi.getById(String(id));
      setMember(refreshed);
      setError('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to update administrator:', err);
      setError('Erro ao atualizar administrador');
    }
  };

  const handleChangePassword = async () => {
    if (!newPassword.trim()) {
      setError('Password é obrigatória');
      return;
    }

    try {
      await administratorsApi.changePassword(String(id), {
        new_password: newPassword,
        temporary: false,
      });
      setNewPassword('');
      setError('');
      setIsPasswordModalOpen(false);
      alert('Password alterada com sucesso!');
    } catch (err) {
      console.error('Failed to change password:', err);
      setError('Erro ao alterar password');
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Tem certeza que deseja eliminar este administrador?')) {
      try {
        await administratorsApi.delete(String(id));
        navigate('/geral/administradores');
      } catch (err) {
        console.error('Failed to delete administrator:', err);
        setError('Erro ao eliminar administrador');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!member) return null;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 p-8 max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="space-y-6">
            <div>
              <label className="block text-teal-500 font-medium mb-2">Username</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.username}</div>
            </div>
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.first_name} {member.last_name}</div>
            </div>
            <div>
              <label className="block text-teal-500 font-medium mb-2">Email</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.email}</div>
            </div>
            <div>
              <label className="block text-teal-500 font-medium mb-2">Estado</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
                {member.enabled ? (
                  <span className="text-green-600 font-medium">Ativo</span>
                ) : (
                  <span className="text-red-600 font-medium">Inativo</span>
                )}
              </div>
            </div>
            <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Tipo
                </label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {member.role === 'general_admin' ? 'Geral' :
                   member.role === 'nucleo_admin' ? 'Núcleo' : 'N/A'}
                </div>
            </div>

            {member.role === 'nucleo_admin' && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Núcleos</label>
                <div className="bg-gray-100 px-4 py-3 rounded-md">
                  {member.nucleos.length === 0 ? (
                    <span className="text-gray-500">Nenhum núcleo associado</span>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {member.nucleos.map(nucleo => (
                        <span
                          key={nucleo.id}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-teal-100 text-teal-800 font-medium"
                        >
                          {nucleo.name} <span className="ml-1 text-teal-600">({nucleo.abbreviation})</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={handleEdit} className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium">
              Editar
            </button>
            <button onClick={() => setIsPasswordModalOpen(true)} className="flex-1 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium">
              Alterar Password
            </button>
            <button onClick={handleDelete} className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium">
              Eliminar
            </button>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Administrador</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
            <div>
                <label className="block text-gray-700 font-medium mb-2">Username</label>
                <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                  {editedUserName}
                </div>
                <p className="text-xs text-gray-500 mt-1">O username não pode ser alterado</p>
            </div>
            <div>
                <label className="block text-gray-700 font-medium mb-2">Primeiro Nome <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  value={editedFirstName}
                  onChange={(e) => setEditedFirstName(e.target.value)}
                  placeholder="Digite o primeiro nome"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
            <div>
                <label className="block text-gray-700 font-medium mb-2">Último Nome <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  value={editedLastName}
                  onChange={(e) => setEditedLastName(e.target.value)}
                  placeholder="Digite o último nome"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
            <div>
                <label className="block text-gray-700 font-medium mb-2">Email <span className="text-red-500">*</span></label>
                <input
                  type="email"
                  value={editedEmail}
                  onChange={(e) => setEditedEmail(e.target.value)}
                  placeholder="Digite o email"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
            <div>
                <label className="block text-gray-700 font-medium mb-2">Estado</label>
                <select
                  value={editedEnabled ? 'true' : 'false'}
                  onChange={(e) => setEditedEnabled(e.target.value === 'true')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                >
                  <option value="true">Ativo</option>
                  <option value="false">Inativo</option>
                </select>
            </div>

            <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo
                </label>
                <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                  {member.role === 'general_admin' ? 'Geral' :
                   member.role === 'nucleo_admin' ? 'Núcleo' : 'N/A'}
                </div>
                <p className="text-xs text-gray-500 mt-1">O tipo não pode ser alterado</p>
            </div>

            {member.role === 'nucleo_admin' && (
              <div>
                <label className="block text-gray-700 font-medium mb-2">Núcleos</label>
                <div className="border border-gray-300 rounded-md max-h-40 overflow-y-auto p-2 space-y-1">
                  {allNucleos.length === 0 ? (
                    <p className="text-gray-500 text-sm p-2">A carregar núcleos...</p>
                  ) : (
                    allNucleos.map((nucleo) => (
                      <label key={nucleo.id} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-50 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={editedNucleos.includes(nucleo.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setEditedNucleos([...editedNucleos, nucleo.id]);
                            } else {
                              setEditedNucleos(editedNucleos.filter(nid => nid !== nucleo.id));
                            }
                          }}
                          className="accent-teal-500"
                        />
                        <span className="text-gray-800">{nucleo.name}</span>
                        <span className="text-gray-500 text-sm">({nucleo.abbreviation})</span>
                      </label>
                    ))
                  )}
                </div>
              </div>
            )}
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setError('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}

      {isPasswordModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Alterar Password</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">Nova Password <span className="text-red-500">*</span></label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Digite a nova password"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsPasswordModalOpen(false);
                  setNewPassword('');
                  setError('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={handleChangePassword}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md"
              >
                Alterar Password
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDetail;
