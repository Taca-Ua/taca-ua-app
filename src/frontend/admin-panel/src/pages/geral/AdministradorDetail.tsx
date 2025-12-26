import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from '../../components/geral_navbar';
import { administratorsApi, type Administrator } from '../../api/administrators';
import { coursesApi, type Course } from '../../api/courses';

function AdminDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [member, setMember] = useState<Administrator | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [editedUserName, setEditedUserName] = useState('');
  const [editedFullName, setEditedFullName] = useState('');
  const [editedEmail, setEditedEmail] = useState('');
  const [editedPassword, setEditedPassword] = useState('');
  const [editedCourseId, setEditedCourseId] = useState<number | ''>('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [adminData, coursesData] = await Promise.all([
          administratorsApi.getById(Number(id)),
          coursesApi.getAll(),
        ]);
        setMember(adminData);
        setCourses(coursesData);
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
    setEditedFullName(member.full_name);
    setEditedEmail(member.email);
    setEditedPassword('');
    setEditedCourseId(member.course_id || '');
    setError('');
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!editedUserName.trim()) {
      setError('Username é obrigatório');
      return;
    }
    if (!editedFullName.trim()) {
      setError('Nome é obrigatório');
      return;
    }
    if (!editedEmail.trim()) {
      setError('Email é obrigatório');
      return;
    }
    if (member?.role === 'nucleo' && !editedCourseId) {
      setError('Núcleo é obrigatório para administrador de núcleo');
      return;
    }

    try {
      const updatedAdmin = await administratorsApi.update(Number(id), {
        username: editedUserName,
        full_name: editedFullName,
        email: editedEmail,
        password: editedPassword || undefined,
        course_id: editedCourseId ? Number(editedCourseId) : undefined,
      });
      setMember(updatedAdmin);
      setError('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to update administrator:', err);
      setError('Erro ao atualizar administrador');
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Tem certeza que deseja eliminar este administrador?')) {
      try {
        await administratorsApi.delete(Number(id));
        navigate('/geral/administradores');
      } catch (err) {
        console.error('Failed to delete administrator:', err);
        setError('Erro ao eliminar administrador');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!member) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="p-8 max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="space-y-6">
            {/* UserName */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Username</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.username}</div>
            </div>
            {/* Name */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.full_name}</div>
            </div>
            {/* Email */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Email</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.email}</div>
            </div>
            {/* Password */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Password</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800 flex items-center justify-between">
                <span className="font-mono">
                  {showPassword ? member.password : '••••••••'}
                </span>
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="ml-4 text-teal-600 hover:text-teal-700 focus:outline-none"
                  type="button"
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            {/* Type */}
            <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Tipo
                </label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {member.role === 'geral' ? 'Geral' : 'Núcleo'}
                </div>
            </div>
            {/* Nucleo */}
            {member.role === 'nucleo' && (
              <div>
                <label className="block text-teal-500 font-medium mb-2">Núcleo</label>
                <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.course_abbreviation || 'N/A'}</div>
              </div>
            )}
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={handleEdit} className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium">
              Editar
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
            {/* Username */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">Username <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  value={editedUserName}
                  onChange={(e) => setEditedUserName(e.target.value)}
                  placeholder="Digite o username"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
            {/* Full Name */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">Nome <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  value={editedFullName}
                  onChange={(e) => setEditedFullName(e.target.value)}
                  placeholder="Digite o nome completo"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
            {/* Password */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">Password (deixe em branco para manter)</label>
                <input
                  type="password"
                  value={editedPassword}
                  onChange={(e) => setEditedPassword(e.target.value)}
                  placeholder="Digite a nova password"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
              {/* Email */}
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

            {/* Role Display (non-editable) */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo
                </label>
                <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                  {member.role === 'geral' ? 'Geral' : 'Núcleo'}
                </div>
            </div>


            {/* Nucleo */}
            {member.role === 'nucleo' && (
                <div>
                  <label className="block text-gray-700 font-medium mb-2">Núcleo <span className="text-red-500">*</span></label>
                  <select
                    value={editedCourseId}
                    onChange={(e) => setEditedCourseId(Number(e.target.value))}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  >
                  <option value="">Selecionar Núcleo</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.abbreviation} - {course.name}
                    </option>
                  ))}
                  </select>
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
    </div>
  );
}

export default AdminDetail;
