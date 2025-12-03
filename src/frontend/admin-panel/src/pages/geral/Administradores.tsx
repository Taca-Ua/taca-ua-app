import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Admin {
  id: number;
  name: string;
  role: 'geral' | 'nucleo';
  nmec: string;
  nucleoName?: string;
}

function Administradores() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [memberName, setMemberName] = useState('');
  const [memberRole, setMemberRole] = useState<'geral' | 'nucleo'>('geral');
  const [nmec, setNmec] = useState('');
  const [nucleo, setNucleo] = useState('');

  // Mock data
  const [members, setMembers] = useState<Admin[]>([
    { id: 1, name: 'AdminG 1', role: 'geral', nmec: '12345' },
    { id: 2, name: 'AdminG 2', role: 'geral', nmec: '23456' },
    { id: 3, name: 'AdminG 3', role: 'geral', nmec: '34567' },
    { id: 4, name: 'AdminG 4', role: 'geral', nmec: '45678' },
    { id: 5, name: 'AdminG 5', role: 'geral', nmec: '56789' },
    { id: 6, name: 'AdminN 1', role: 'nucleo', nmec: '67890', nucleoName: 'Núcleo A' },
    { id: 7, name: 'AdminN 2', role: 'nucleo', nmec: '78901', nucleoName: 'Núcleo B' },
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
    if (!memberName.trim()) return;
    if (!nmec.trim()) return;
    if (memberRole === 'nucleo' && !nucleo.trim()) return;

    const newMember: Admin = {
      id: members.length + 1,
      name: memberName,
      role: memberRole,
      nmec,
      ...(memberRole === 'nucleo' ? { nucleoName: nucleo } : {}),
    };

    setMembers([...members, newMember]);
    setMemberName('');
    setMemberRole('geral');
    setNmec('');
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
                    <span className="text-gray-800 font-medium">{AdminG.name}</span>
                    <span className="text-gray-600 text-sm">NMEC: {AdminG.nmec}</span>
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
                      NMEC: {AdminN.nmec} | Núcleo: {AdminN.nucleoName}
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
              {/* Nombre */}
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
                  placeholder="Digite o nome do membro"
                />
              </div>

              {/* Role */}
              <div>
                <label htmlFor="memberRole" className="block text-gray-700 font-medium mb-2">
                  Tipo
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

              {/* NMEC */}
              <div>
                <label htmlFor="nmec" className="block text-gray-700 font-medium mb-2">
                  NMEC <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="nmec"
                  value={nmec}
                  onChange={(e) => setNmec(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o NMEC (ex: 12345)"
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
                  setMemberName('');
                  setMemberRole('geral');
                  setNmec('');
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
