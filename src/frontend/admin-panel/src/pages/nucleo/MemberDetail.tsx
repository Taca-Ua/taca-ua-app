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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [member, setMember] = useState<Member | null>(null);
  const [editedName, setEditedName] = useState('');
  const [editedNmec, setEditedNmec] = useState('');
  const [editedContact, setEditedContact] = useState('');
  const [identifierType, setIdentifierType] = useState<'contact' | 'nmec'>('nmec');

  useEffect(() => {
    // TODO: Replace with API call
    const foundMember = mockMembers.find(m => m.id === parseInt(id || '0'));
    if (foundMember) {
      setMember(foundMember);
    } else {
      // Redirect to members page if member not found
      navigate('/nucleo/membros');
    }
  }, [id, navigate]);

  if (!member) {
    return null;
  }

  const handleEdit = () => {
    setEditedName(member.name);
    setEditedNmec(member.nmec || '');
    setEditedContact(member.contact || '');
    setIdentifierType(member.nmec ? 'nmec' : 'contact');
    setIsModalOpen(true);
  };

  const handleSave = () => {
    if (!editedName.trim()) return;
    
    // Validation based on role
    if (member.role === 'jogador' && !editedNmec.trim()) return;
    if (member.role === 'tecnico' && !((identifierType === 'contact' && editedContact.trim()) || (identifierType === 'nmec' && editedNmec.trim()))) return;

    const updatedMember: Member = {
      ...member,
      name: editedName,
      ...(member.role === 'jogador' 
        ? { nmec: editedNmec, contact: undefined } 
        : (identifierType === 'contact' ? { contact: editedContact, nmec: undefined } : { nmec: editedNmec, contact: undefined })
      ),
    };
    
    // TODO: API call to update member
    setMember(updatedMember);
    setIsModalOpen(false);
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
            {/* Member Details - Read Only */}
            <div className="space-y-6">
              {/* Name */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Nome
                </label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {member.name}
                </div>
              </div>

              {/* NMec/Contacto */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  NMec/Contacto
                </label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {member.nmec || member.contact}
                </div>
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
              <button
                onClick={handleEdit}
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
            </div>
          </div>
        </div>
      </div>

      {/* Edit Member Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Membro</h2>
            
            <div className="space-y-4">
              {/* Name Input */}
              <div>
                <label htmlFor="editName" className="block text-gray-700 font-medium mb-2">
                  Nome
                </label>
                <input
                  type="text"
                  id="editName"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome do membro"
                />
              </div>

              {/* Role Display (non-editable) */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Tipo
                </label>
                <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                  {member.role === 'jogador' ? 'Jogador' : 'Técnico'}
                </div>
              </div>

              {/* Identifier Type Selection - Only for Técnicos */}
              {member.role === 'tecnico' && (
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Identificação
                  </label>
                  <div className="flex gap-4 mb-3">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="identifierType"
                        value="contact"
                        checked={identifierType === 'contact'}
                        onChange={() => setIdentifierType('contact')}
                        className="mr-2"
                      />
                      <span className="text-gray-700">Contacto</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="identifierType"
                        value="nmec"
                        checked={identifierType === 'nmec'}
                        onChange={() => setIdentifierType('nmec')}
                        className="mr-2"
                      />
                      <span className="text-gray-700">NMEC</span>
                    </label>
                  </div>

                  {/* Contact or NMEC Input */}
                  {identifierType === 'contact' ? (
                    <input
                      type="tel"
                      value={editedContact}
                      onChange={(e) => setEditedContact(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o contacto (ex: 912345678)"
                    />
                  ) : (
                    <input
                      type="text"
                      value={editedNmec}
                      onChange={(e) => setEditedNmec(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o NMEC (ex: 12345)"
                    />
                  )}
                </div>
              )}

              {/* NMEC Input - Required for Jogadores */}
              {member.role === 'jogador' && (
                <div>
                  <label htmlFor="editNmec" className="block text-gray-700 font-medium mb-2">
                    NMEC <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="editNmec"
                    value={editedNmec}
                    onChange={(e) => setEditedNmec(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Digite o NMEC (ex: 12345)"
                  />
                  <p className="text-sm text-gray-500 mt-1">Jogadores devem ser estudantes</p>
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setEditedName('');
                  setEditedNmec('');
                  setEditedContact('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
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

export default MemberDetail;
