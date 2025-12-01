import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import NucleoSidebar from '../../components/nucleo_navbar';

interface Member {
  id: number;
  name: string;
  role: 'jogador' | 'tecnico';
  contact?: string;
  nmec?: string;
}

// Mock data - should match the data in Membros.tsx
const mockMembers: Member[] = [
  { id: 1, name: 'Jogador 1', role: 'jogador', nmec: '12345' },
  { id: 2, name: 'Jogador 2', role: 'jogador', nmec: '23456' },
  { id: 3, name: 'Jogador 3', role: 'jogador', nmec: '34567' },
  { id: 4, name: 'Jogador 4', role: 'jogador', nmec: '45678' },
  { id: 5, name: 'Jogador 5', role: 'jogador', nmec: '56789' },
  { id: 6, name: 'Tecnico 1', role: 'tecnico', contact: '915678901' },
  { id: 7, name: 'Tecnico 2', role: 'tecnico', nmec: '67890' },
  { id: 8, name: 'Tecnico 3', role: 'tecnico', contact: '916789012' },
  { id: 9, name: 'Tecnico 4', role: 'tecnico', nmec: '78901' },
];

function MemberDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [member, setMember] = useState<Member | null>(null);
  const [editedMember, setEditedMember] = useState<Member | null>(null);

  useEffect(() => {
    // TODO: Replace with API call
    const foundMember = mockMembers.find(m => m.id === parseInt(id || '0'));
    if (foundMember) {
      setMember(foundMember);
      setEditedMember(foundMember);
    } else {
      // Redirect to members page if member not found
      navigate('/nucleo/membros');
    }
  }, [id, navigate]);

  if (!member || !editedMember) {
    return null;
  }

  const handleSave = () => {
    // TODO: API call to update member
    setMember(editedMember);
    setIsEditing(false);
  };

  const handleDelete = () => {
    // TODO: Add confirmation modal
    if (window.confirm('Tem certeza que deseja eliminar este membro?')) {
      // TODO: API call to delete member
      navigate('/nucleo/membros');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="p-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8">
            {/* Member Details Form */}
            <div className="space-y-6">
              {/* Name */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Nome
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedMember.name}
                    onChange={(e) => setEditedMember({ ...editedMember, name: e.target.value })}
                    className="w-full px-4 py-3 bg-gray-100 rounded-md border-2 border-gray-300 focus:outline-none focus:border-teal-500"
                  />
                ) : (
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {member.name}
                  </div>
                )}
              </div>

              {/* NMec/Contacto */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  NMec/Contacto
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedMember.nmec || editedMember.contact || ''}
                    onChange={(e) => {
                      if (member.nmec !== undefined) {
                        setEditedMember({ ...editedMember, nmec: e.target.value });
                      } else {
                        setEditedMember({ ...editedMember, contact: e.target.value });
                      }
                    }}
                    className="w-full px-4 py-3 bg-gray-100 rounded-md border-2 border-gray-300 focus:outline-none focus:border-teal-500"
                    disabled={member.role === 'jogador'}
                  />
                ) : (
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {member.nmec || member.contact}
                  </div>
                )}
                {member.role === 'jogador' && isEditing && (
                  <p className="text-sm text-gray-500 mt-1">Jogadores devem ter NMEC (não editável)</p>
                )}
              </div>

              {/* Type */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Tipo
                </label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {member.role === 'jogador' ? 'Jogador' : 'Técnico'}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-8">
              {isEditing ? (
                <>
                  <button
                    onClick={() => {
                      setEditedMember(member);
                      setIsEditing(false);
                    }}
                    className="flex-1 px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSave}
                    className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                  >
                    Guardar
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex-1 px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                  >
                    Editar
                  </button>
                  <button
                    onClick={handleDelete}
                    className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
                  >
                    Eliminar
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MemberDetail;
