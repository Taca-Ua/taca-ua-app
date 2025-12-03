import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Admin {
  id: number;
  username: string;
  name?: string;
  email: string;
  role: 'geral' | 'nucleo';
  nucleoName?: string;
}

function Administradores() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [memberUserName, setMemberUserName] = useState('');
  const [memberName, setMemberName] = useState('');
  const [memberRole, setMemberRole] = useState<'geral' | 'nucleo'>('geral');
  const [email, setEmail] = useState('');
  const [nucleo, setNucleo] = useState('');

  // Mock data
  const [members, setMembers] = useState<Admin[]>([
    { id: 1, username: 'AdminG1', role: 'geral',email: 'admin1@ua.pt', name: 'admin geral 1' },
    { id: 2, username: 'AdminG2', role: 'geral',email: 'admin2@ua.pt', name: 'admin geral 2' },
    { id: 3, username: 'AdminG3', role: 'geral',email: 'admin3@ua.pt', name: 'admin geral 3' },
    { id: 4, username: 'AdminG4', role: 'geral',email: 'admin4@ua.pt', name: 'admin geral 4' },
    { id: 5, username: 'AdminG5', role: 'geral',email: 'admin5@ua.pt', name: 'admin geral 5'},
    { id: 6, username: 'AdminN1', role: 'nucleo',email: 'admin6@ua.pt', name: 'admin nucleo 1', nucleoName: 'Núcleo A' },
    { id: 7, username: 'AdminN2', role: 'nucleo',email: 'admin7@ua.pt', name: 'admin nucleo 2' , nucleoName: 'Núcleo B' },
  ]);

  // TODO: Replace with real NUCLEOS from API
  const nucleos = [
    'NEI',
    'NECIB',
    'NEG',
    'NEMAT',
    'NECM',
    'NEGEO',
  ];

  const AdminG = members.filter(m => m.role === 'geral');
  const AdminN = members.filter(m => m.role === 'nucleo');

  const handleAddMember = () => {
    if (!memberUserName.trim()) return;
    if (!email.trim()) return;
    if (memberRole === 'nucleo' && !nucleo.trim()) return;

    const newMember: Admin = {
      id: members.length + 1,
      username: memberUserName,
      name: memberName,
      role: memberRole,
      email,
      ...(memberRole === 'nucleo' ? { nucleoName: nucleo } : {}),
    };

    setMembers([...members, newMember]);
    setMemberUserName('');
    setMemberRole('geral');
    setEmail('');
    setNucleo('');
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-end mb-6">
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Membros
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
                    <span className="text-gray-800 font-medium">{AdminN.name}</span>
                    <span className="text-gray-600 text-sm">
                      NMEC: {AdminN.email} | Núcleo: {AdminN.nucleoName}
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
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Membro</h2>

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
                  placeholder="Digite o nome do membro"
                />
              </div>

               {/* Nome */}
               <div>
                <label htmlFor="memberName" className="block text-gray-700 font-medium mb-2">
                  Nome
                </label>
                <input
                  type="text"
                  id="memberName"
                  value={memberName}
                  onChange={(e) => setMemberName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome do membro"
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
                  <label htmlFor="nucleo" className="block text-gray-700 font-medium mb-2">
                    Núcleo <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="nucleo"
                    value={nucleo}
                    onChange={(e) => setNucleo(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                  <option value="">Selecionar Nucleo</option>
                  {nucleos.map((nucleos) => (
                    <option key={nucleos} value={nucleos}>
                      {nucleos}
                    </option>
                  ))}
                  </select>
                </div>
              )}
            </div>

            {/* Botones */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setMemberUserName('');
                  setMemberRole('geral');
                  setEmail('');
                  setNucleo('');
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
