import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ConfirmModal from '../../components/ConfirmModal';
import Sidebar from '../../components/geral_navbar';
import { administratorsApi, type AdminDetails } from '../../api/administrators';
import { nucleosApi, type Nucleo } from '../../api/nucleos';
import { coursesApi, type Course } from '../../api/courses';
import { useNotification } from '../../contexts/NotificationProvider';

function AdminDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [member, setMember] = useState<AdminDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();

  const [editedUserName, setEditedUserName] = useState('');
  const [editedFirstName, setEditedFirstName] = useState('');
  const [editedLastName, setEditedLastName] = useState('');
  const [editedEmail, setEditedEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [editedEnabled, setEditedEnabled] = useState(true);
  const [allNucleos, setAllNucleos] = useState<Nucleo[]>([]);
  const [editedNucleos, setEditedNucleos] = useState<string[]>([]);
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);
  const [nucleoSearchEdit, setNucleoSearchEdit] = useState('');
  const [adminCourses, setAdminCourses] = useState<Course[]>([]);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const adminData = await administratorsApi.getById(String(id));
        setMember(adminData);
        if (adminData.role === 'nucleo_admin' && adminData.nucleos.length > 0) {
          const allCourses = await coursesApi.getAll();
          const nucleoIds = new Set(adminData.nucleos.map((n: Nucleo) => n.id));
          setAdminCourses(allCourses.filter(c => nucleoIds.has(c.nucleo.id)));
        }
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

  const handleEdit = () => {
    if (!member) return;
    setEditedUserName(member.username);
    setEditedFirstName(member.first_name);
    setEditedLastName(member.last_name);
    setEditedEmail(member.email);
    setEditedEnabled(member.enabled);
    setEditedNucleos(member.nucleos.map(n => n.id));
    // Fetch all nucleos for the selector
    nucleosApi.getAll().then(setAllNucleos).catch(console.error);
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!member) return;
    if (!editedEmail.trim()) {
      notify('Email é obrigatório', 'error');
      return;
    }
    if (!editedFirstName.trim()) {
      notify('Primeiro nome é obrigatório', 'error');
      return;
    }
    if (!editedLastName.trim()) {
      notify('Último nome é obrigatório', 'error');
      return;
    }

    try {
      console.log('Saving with nucleos:', editedNucleos);
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
      if (refreshed.role === 'nucleo_admin') {
        const allCourses = await coursesApi.getAll();
        const nucleoIds = new Set(refreshed.nucleos.map(n => n.id));
        setAdminCourses(allCourses.filter(c => nucleoIds.has(c.nucleo.id)));
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to update administrator:', err);
      notify('Não foi possível guardar as alterações ao administrador. Verifique os dados e tente novamente.', 'error');
    }
  };

  const handleChangePassword = async () => {
    if (!newPassword.trim()) {
      notify('Password é obrigatória', 'error');
      return;
    }
    if (!confirmNewPassword.trim()) {
      notify('Confirmação de password é obrigatória', 'error');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      notify('As passwords não coincidem', 'error');
      return;
    }

    try {
      await administratorsApi.changePassword(String(id), {
        new_password: newPassword,
        temporary: false,
      });
      setNewPassword('');
      setConfirmNewPassword('');
      setShowNewPassword(false);
      setShowConfirmNewPassword(false);
      setIsPasswordModalOpen(false);
      notify('Password alterada com sucesso!', 'success');
    } catch (err) {
      console.error('Failed to change password:', err);
      notify('Não foi possível alterar a password. Certifique-se que a password atual está correta.', 'error');
    }
  };

  const handleDelete = () => {
    setIsDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    try {
      setDeleting(true);
      await administratorsApi.delete(String(id));
      navigate('/geral/administradores');
    } catch (err) {
      console.error('Failed to delete administrator:', err);
      notify('Não foi possível eliminar o administrador. Tente novamente.', 'error');
    } finally {
      setDeleting(false);
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
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes do Administrador</h1>
          <button
            onClick={() => navigate('/geral/administradores')}
            className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            Voltar
          </button>
        </div>

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

            {member.role === 'nucleo_admin' && adminCourses.length > 0 && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Cursos Associados</label>
                <div className="bg-gray-100 px-4 py-3 rounded-md">
                  <div className="flex flex-wrap gap-2">
                    {adminCourses.map(course => (
                      <span key={course.id} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 font-medium">
                        {course.name}<span className="ml-1 text-blue-600">({course.abbreviation})</span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={handleEdit} className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-teal-400">
              Editar
            </button>
            <button onClick={() => setIsPasswordModalOpen(true)} className="flex-1 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-blue-400">
              Alterar Password
            </button>
            <button onClick={handleDelete} className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-red-400">
              Eliminar
            </button>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Administrador</h2>

            <div className="overflow-y-auto flex-1 pr-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label className="block text-gray-700 font-medium mb-2">Username</label>
                <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                  {editedUserName}
                </div>
                <p className="text-xs text-gray-500 mt-1">O username não pode ser alterado</p>
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
            </div>

            {member.role === 'nucleo_admin' && (
              <div className="mt-4">
                <label className="block text-gray-700 font-medium mb-2">Núcleos</label>
                <input
                  type="text"
                  value={nucleoSearchEdit}
                  onChange={(e) => setNucleoSearchEdit(e.target.value)}
                  placeholder="Pesquisar núcleo..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 mb-2"
                />
                <div className="border border-gray-300 rounded-md max-h-40 overflow-y-auto p-2 space-y-1">
                  {allNucleos.length === 0 ? (
                    <p className="text-gray-500 text-sm p-2">A carregar núcleos...</p>
                  ) : (
                    [...allNucleos]
                      .sort((a, b) => a.name.localeCompare(b.name))
                      .filter(n => n.name.toLowerCase().includes(nucleoSearchEdit.toLowerCase()) || n.abbreviation.toLowerCase().includes(nucleoSearchEdit.toLowerCase()))
                      .map((nucleo) => (
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

            <div className="flex gap-4 mt-6 flex-shrink-0">
              <button
                onClick={() => {
                  setIsModalOpen(false);
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

            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">Nova Password <span className="text-red-500">*</span></label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Digite a nova password"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 pr-10"
                  />
                  <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
                    {showNewPassword
                      ? <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    }
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2">Confirmar Password <span className="text-red-500">*</span></label>
                <div className="relative">
                  <input
                    type={showConfirmNewPassword ? 'text' : 'password'}
                    value={confirmNewPassword}
                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                    placeholder="Confirme a nova password"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 pr-10"
                  />
                  <button type="button" onClick={() => setShowConfirmNewPassword(!showConfirmNewPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
                    {showConfirmNewPassword
                      ? <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      : <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    }
                  </button>
                </div>
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsPasswordModalOpen(false);
                  setNewPassword('');
                  setConfirmNewPassword('');
                  setShowNewPassword(false);
                  setShowConfirmNewPassword(false);
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

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        title="Eliminar administrador"
        message="Tem certeza que deseja eliminar este administrador?"
        confirmLabel="Eliminar"
        variant="danger"
        loading={deleting}
        onCancel={() => {
          if (!deleting) {
            setIsDeleteModalOpen(false);
          }
        }}
        onConfirm={confirmDelete}
      />
    </div>
  );
}

export default AdminDetail;
