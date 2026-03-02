import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { administratorsApi, type Admin } from '../../api/administrators';
import { nucleosApi, type Nucleo } from '../../api/nucleos';

function Administradores() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [memberUserName, setMemberUserName] = useState('');
  const [memberFirstName, setMemberFirstName] = useState('');
  const [memberLastName, setMemberLastName] = useState('');
  const [memberPassword, setMemberPassword] = useState('');
  const [memberRole, setMemberRole] = useState<'general_admin' | 'nucleo_admin'>('general_admin');
  const [email, setEmail] = useState('');

  const [members, setMembers] = useState<Admin[]>([]);
  const [allNucleos, setAllNucleos] = useState<Nucleo[]>([]);
  const [selectedNucleos, setSelectedNucleos] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [adminsData, nucleosData] = await Promise.all([
          administratorsApi.getAll(),
          nucleosApi.getAll(),
        ]);
        setMembers(adminsData);
        setAllNucleos(nucleosData);
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

  const AdminG = members.filter(m => m.role === 'general_admin');
  const AdminN = members.filter(m => m.role === 'nucleo_admin');

  const handleAddMember = async () => {
    if (!memberUserName.trim()) {
      setError('Username é obrigatório');
      return;
    }
    if (!memberFirstName.trim()) {
      setError('Primeiro nome é obrigatório');
      return;
    }
    if (!memberLastName.trim()) {
      setError('Último nome é obrigatório');
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

    try {
      const newAdmin = await administratorsApi.create({
        username: memberUserName,
        password: memberPassword,
        first_name: memberFirstName,
        last_name: memberLastName,
        email,
        role: memberRole,
        nucleos: memberRole === 'nucleo_admin' ? selectedNucleos : [],
      });

      setMembers([...members, newAdmin]);
      setMemberUserName('');
      setMemberFirstName('');
      setMemberLastName('');
      setMemberPassword('');
      setMemberRole('general_admin');
      setEmail('');
      setSelectedNucleos([]);
      setError('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create administrator:', err);
      setError('Erro ao criar administrador');
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

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 p-8">
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

          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Administradores Gerais</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {AdminG.map((admin) => (
                <div
                  key={admin.id}
                  onClick={() => navigate(`/geral/administradores/${admin.id}`)}
                  className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{admin.username}</span>
                    <span className="text-gray-600 text-sm">{admin.first_name} {admin.last_name} - {admin.email}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Administradores Núcleo</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {AdminN.map((admin) => (
                <div
                  key={admin.id}
                  onClick={() => navigate(`/geral/administradores/${admin.id}`)}
                  className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{admin.username}</span>
                    <span className="text-gray-600 text-sm">{admin.first_name} {admin.last_name} - {admin.email}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 animate-slideUp max-h-[90vh] overflow-hidden flex flex-col">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Administrador</h2>

            <div className="overflow-y-auto flex-1 pr-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <div>
                <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o email (ex: admin@ua.pt)"
                />
              </div>
              <div>
                <label htmlFor="memberFirstName" className="block text-gray-700 font-medium mb-2">
                  Primeiro Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="memberFirstName"
                  value={memberFirstName}
                  onChange={(e) => setMemberFirstName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o primeiro nome"
                />
              </div>

              <div>
                <label htmlFor="memberLastName" className="block text-gray-700 font-medium mb-2">
                  Último Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="memberLastName"
                  value={memberLastName}
                  onChange={(e) => setMemberLastName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o último nome"
                />
              </div>

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
              <div>
                <label htmlFor="memberRole" className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
                </label>
                <select
                  id="memberRole"
                  value={memberRole}
                  onChange={(e) => {
                    setMemberRole(e.target.value as 'general_admin' | 'nucleo_admin');
                    setSelectedNucleos([]);
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="general_admin">Administrador Geral</option>
                  <option value="nucleo_admin">Administrador Núcleo</option>
                </select>
              </div>
            </div>

              {memberRole === 'nucleo_admin' && (
                <div className="mt-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    Núcleos
                  </label>
                  <div className="border border-gray-300 rounded-md max-h-40 overflow-y-auto p-2 space-y-1">
                    {allNucleos.length === 0 ? (
                      <p className="text-gray-500 text-sm p-2">Nenhum núcleo disponível</p>
                    ) : (
                      allNucleos.map((nucleo) => (
                        <label key={nucleo.id} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-50 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedNucleos.includes(nucleo.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedNucleos([...selectedNucleos, nucleo.id]);
                              } else {
                                setSelectedNucleos(selectedNucleos.filter(id => id !== nucleo.id));
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

            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            <div className="flex gap-4 mt-6 flex-shrink-0">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setMemberUserName('');
                  setMemberFirstName('');
                  setMemberLastName('');
                  setMemberPassword('');
                  setMemberRole('general_admin');
                  setEmail('');
                  setSelectedNucleos([]);
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
