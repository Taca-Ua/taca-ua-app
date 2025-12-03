import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useMemo } from 'react';
import Sidebar from '../../components/geral_navbar';
interface Admin {
  id: number;
  username: string;
  name?: string;
  email: string;
  role: 'geral' | 'nucleo';
  nucleoName?: string;
}

const mockAdmins: Admin[] = [
  { id: 1, username: 'AdminG1', role: 'geral',email: 'admin1@ua.pt', name: 'admin geral 1' },
  { id: 2, username: 'AdminG2', role: 'geral',email: 'admin2@ua.pt', name: 'admin geral 2' },
  { id: 3, username: 'AdminG3', role: 'geral',email: 'admin3@ua.pt', name: 'admin geral 3' },
  { id: 4, username: 'AdminG4', role: 'geral',email: 'admin4@ua.pt', name: 'admin geral 4' },
  { id: 5, username: 'AdminG5', role: 'geral',email: 'admin5@ua.pt', name: 'admin geral 5'},
  { id: 6, username: 'AdminN1', role: 'nucleo',email: 'admin6@ua.pt', name: 'admin nucleo 1', nucleoName: 'Núcleo A' },
  { id: 7, username: 'AdminN2', role: 'nucleo',email: 'admin7@ua.pt', name: 'admin nucleo 2' , nucleoName: 'Núcleo B' },
];

  // TODO: Replace with real NUCLEOS from API
  const nucleos = [
    'NEI',
    'NECIB',
    'NEG',
    'NEMAT',
    'NECM',
    'NEGEO',
  ];

function AdminDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editedUserName, setEditedUserName] = useState('');
  const [editedEmail, setEditedEmail] = useState('');
  const [editedNucleo, setEditedNucleo] = useState('');

  const member = useMemo(() => {
    return mockAdmins.find(m => m.id === parseInt(id || '0')) || null;
  }, [id]);

  useEffect(() => {
    if (!member) navigate('/geral/administradores');
  }, [member, navigate]);

  if (!member) return null;

  const handleEdit = () => {
    setEditedUserName(member.username);
    setEditedEmail(member.email);
    setEditedNucleo(member.nucleoName || '');
    setIsModalOpen(true);
  };

  const handleSave = () => {
    if (!editedUserName.trim() || !editedEmail.trim()) return;
    if (member.role === 'nucleo' && !editedNucleo.trim()) return;

    // TODO: API call to update member
    setIsModalOpen(false);
  };

  const handleDelete = () => {
    if (window.confirm('Tem certeza que deseja eliminar este membro?')) {
      // TODO: API call to delete member
      navigate('/geral/administradores');
    }
  };

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
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.name}</div>
            </div>
            {/* Email */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Email</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.email}</div>
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
                <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.nucleoName}</div>
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
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Membro</h2>
            <div className="space-y-4">
            {/* Username */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">Username</label>
                <input
                  type="text"
                  value={editedUserName}
                  onChange={(e) => setEditedUserName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
              {/* Email */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">Email</label>
                <input
                  type="text"
                  value={editedEmail}
                  onChange={(e) => setEditedEmail(e.target.value)}
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
                  <label className="block text-gray-700 font-medium mb-2">Núcleo</label>
                  <select
                    value={editedNucleo}
                    onChange={(e) => setEditedNucleo(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
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

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsModalOpen(false)}
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
