import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { administratorsApi, type Administrator } from '../../api/administrators';
import { coursesApi, type Course } from '../../api/courses';

function Administradores() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [memberUserName, setMemberUserName] = useState('');
  const [memberName, setMemberName] = useState('');
  const [memberPassword, setMemberPassword] = useState('');
  const [memberRole, setMemberRole] = useState<'geral' | 'nucleo'>('geral');
  const [email, setEmail] = useState('');
  const [courseId, setCourseId] = useState<number | ''>('');

  const [members, setMembers] = useState<Administrator[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [adminsData, coursesData] = await Promise.all([
          administratorsApi.getAll(),
          coursesApi.getAll(),
        ]);
        setMembers(adminsData);
        setCourses(coursesData);
        setError('');
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Erro ao carregar dados');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const AdminG = members.filter(m => m.role === 'geral');
  const AdminN = members.filter(m => m.role === 'nucleo');

  const handleAddMember = async () => {
    if (!memberUserName.trim()) {
      setError('Username é obrigatório');
      return;
    }
    if (!memberName.trim()) {
      setError('Nome é obrigatório');
      return;
    }
    if (!email.trim()) {
      setError('Email é obrigatório');
      return;
    }
    if (!memberPassword.trim()) {
      setError('Password é obrigatória');
      return;
    }
    if (memberRole === 'nucleo' && !courseId) {
      setError('Núcleo é obrigatório para administrador de núcleo');
      return;
    }

    try {
      const newAdmin = await administratorsApi.create({
        username: memberUserName,
        password: memberPassword,
        full_name: memberName,
        email,
        role: memberRole,
        course_id: memberRole === 'nucleo' ? Number(courseId) : undefined,
      });

      setMembers([...members, newAdmin]);
      setMemberUserName('');
      setMemberName('');
      setMemberPassword('');
      setMemberRole('geral');
      setEmail('');
      setCourseId('');
      setError('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create administrator:', err);
      setError('Erro ao criar administrador');
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">Administradores</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Administrador
            </button>
          </div>

          {/* Administradores Gerais */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Administradores Gerais</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {AdminG.map((AdminG) => (
                <div
                  key={AdminG.id}
                  onClick={() => navigate(`/geral/administradores/${AdminG.id}`)}
                  className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{AdminG.username}</span>
                    <span className="text-gray-600 text-sm">Email: {AdminG.email}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Administradores Núcleo */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Administradores Núcleo</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {AdminN.map((AdminN) => (
                <div
                  key={AdminN.id}
                  onClick={() => navigate(`/geral/administradores/${AdminN.id}`)}
                  className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{AdminN.username}</span>
                    <span className="text-gray-600 text-sm">
                      Email: {AdminN.email} | Núcleo: {AdminN.course_abbreviation || 'N/A'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Add Member Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Administrador</h2>

            <div className="space-y-4">
              {/* Username */}
              <div>
                <label htmlFor="memberUserName" className="block text-gray-700 font-medium mb-2">
                  Username <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="memberUserName"
                  value={memberUserName}
                  onChange={(e) => setMemberUserName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o username"
                />
              </div>

               {/* Nome */}
               <div>
                <label htmlFor="memberName" className="block text-gray-700 font-medium mb-2">
                  Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="memberName"
                  value={memberName}
                  onChange={(e) => setMemberName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome completo"
                />
              </div>

              {/* Password */}
              <div>
                <label htmlFor="memberPassword" className="block text-gray-700 font-medium mb-2">
                  Password <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  id="memberPassword"
                  value={memberPassword}
                  onChange={(e) => setMemberPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite a password"
                />
              </div>

              {/* Role */}
              <div>
                <label htmlFor="memberRole" className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <select
                  id="memberRole"
                  value={memberRole}
                  onChange={(e) => setMemberRole(e.target.value as 'geral' | 'nucleo')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="geral">Administrador Geral</option>
                  <option value="nucleo">Administrador Núcleo</option>
                </select>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o email (ex: admin@ua.pt)"
                />
              </div>

              {/* Núcleo */}
              {memberRole === 'nucleo' && (
                <div>
                  <label htmlFor="courseId" className="block text-gray-700 font-medium mb-2">
                    Núcleo <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="courseId"
                    value={courseId}
                    onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Selecionar Curso</option>
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.abbreviation} - {course.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            {/* Botones */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setMemberUserName('');
                  setMemberName('');
                  setMemberPassword('');
                  setMemberRole('geral');
                  setEmail('');
                  setCourseId('');
                  setError('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddMember}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              >
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Administradores;
