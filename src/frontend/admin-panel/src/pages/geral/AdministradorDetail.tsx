import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useMemo } from 'react';
import Sidebar from '../../components/geral_navbar'; // o NucleoSidebar si estás en vista núcleo

interface Admin {
  id: number;
  name: string;
  role: 'geral' | 'nucleo';
  nmec: string;
  nucleoName?: string;
}

const mockAdmins: Admin[] = [
  { id: 1, name: 'AdminG 1', role: 'geral', nmec: '12345' },
  { id: 2, name: 'AdminG 2', role: 'geral', nmec: '23456' },
  { id: 3, name: 'AdminG 3', role: 'geral', nmec: '34567' },
  { id: 4, name: 'AdminG 4', role: 'geral', nmec: '45678' },
  { id: 5, name: 'AdminG 5', role: 'geral', nmec: '56789' },
  { id: 6, name: 'AdminN 1', role: 'nucleo', nmec: '67890', nucleoName: 'Núcleo A' },
  { id: 7, name: 'AdminN 2', role: 'nucleo', nmec: '78901', nucleoName: 'Núcleo B' },
];

function AdminDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedNmec, setEditedNmec] = useState('');
  const [editedNucleo, setEditedNucleo] = useState('');

  const member = useMemo(() => {
    return mockAdmins.find(m => m.id === parseInt(id || '0')) || null;
  }, [id]);

  useEffect(() => {
    if (!member) navigate('/geral/administradores');
  }, [member, navigate]);

  if (!member) return null;

  const handleEdit = () => {
    setEditedName(member.name);
    setEditedNmec(member.nmec);
    setEditedNucleo(member.nucleoName || '');
    setIsModalOpen(true);
  };

  const handleSave = () => {
    if (!editedName.trim() || !editedNmec.trim()) return;
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
            {/* Name */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">Nome</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.name}</div>
            </div>
            {/* NMec */}
            <div>
              <label className="block text-teal-500 font-medium mb-2">NMEC</label>
              <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">{member.nmec}</div>
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
            {/* Name */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">Nome</label>
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                />
            </div>
              {/* NMec */}
            <div>
                <label className="block text-gray-700 font-medium mb-2">NMEC</label>
                <input
                  type="text"
                  value={editedNmec}
                  onChange={(e) => setEditedNmec(e.target.value)}
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
                  <input
                    type="text"
                    value={editedNucleo}
                    onChange={(e) => setEditedNucleo(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  />
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
