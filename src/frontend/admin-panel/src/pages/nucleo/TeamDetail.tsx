import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';

interface Team {
  id: number;
  name: string;
  modality: string;
  description: string;
  members: number[];
}

interface Member {
  id: number;
  name: string;
}

const TeamDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [team, setTeam] = useState<Team | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedModality, setEditedModality] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null);

  // Mock data for teams (should match Equipas.tsx)
  const mockTeams: Team[] = [
    { id: 1, name: 'Equipa 1', modality: 'Futebol', description: 'Equipa principal de futebol', members: [1, 2, 3, 4, 5, 6, 7, 8, 9] },
    { id: 2, name: 'Equipa 2', modality: 'Basquetebol', description: 'Equipa de basquetebol feminino', members: [2, 4, 6] },
    { id: 3, name: 'Equipa 3', modality: 'Voleibol', description: 'Equipa de voleibol', members: [1, 3, 5] },
    { id: 4, name: 'Equipa 4', modality: 'Futebol', description: 'Equipa secundária de futebol', members: [7, 8, 9] },
    { id: 5, name: 'Equipa 5', modality: 'Futsal', description: 'Equipa de futsal', members: [1, 2] },
    { id: 6, name: 'Equipa 6', modality: 'Andebol', description: 'Equipa de andebol', members: [3, 4] },
    { id: 7, name: 'Equipa 7', modality: 'Rugby', description: 'Equipa de rugby', members: [5, 6] },
    { id: 8, name: 'Equipa 8', modality: 'Basquetebol', description: 'Equipa de basquetebol masculino', members: [7, 8] },
    { id: 9, name: 'Equipa 9', modality: 'Voleibol', description: 'Equipa de voleibol de praia', members: [1, 9] },
  ];

  // Mock data for available members (should match Membros.tsx)
  const mockMembers: Member[] = [
    { id: 1, name: 'João Silva' },
    { id: 2, name: 'Maria Santos' },
    { id: 3, name: 'Pedro Costa' },
    { id: 4, name: 'Ana Ferreira' },
    { id: 5, name: 'Carlos Oliveira' },
    { id: 6, name: 'Sofia Rodrigues' },
    { id: 7, name: 'Miguel Alves' },
    { id: 8, name: 'Inês Pereira' },
    { id: 9, name: 'Ricardo Martins' },
  ];

  const modalities = [
    'Futebol',
    'Futsal',
    'Basquetebol',
    'Voleibol',
    'Andebol',
    'Rugby',
  ];

  useEffect(() => {
    const foundTeam = mockTeams.find((t) => t.id === Number(id));
    if (foundTeam) {
      setTeam(foundTeam);
    } else {
      navigate('/nucleo/equipas');
    }
  }, [id, navigate]);

  if (!team) {
    return null;
  }

  const teamMembers = mockMembers.filter((member) => team.members.includes(member.id));
  const availableMembers = mockMembers.filter((member) => !team.members.includes(member.id));

  const handleEdit = () => {
    setEditedName(team.name);
    setEditedModality(team.modality);
    setEditedDescription(team.description);
    setIsEditModalOpen(true);
  };

  const handleSave = () => {
    if (!editedName.trim()) {
      alert('Por favor, preencha o nome da equipa.');
      return;
    }

    if (!editedModality) {
      alert('Por favor, selecione uma modalidade.');
      return;
    }

    setTeam({
      ...team,
      name: editedName,
      modality: editedModality,
      description: editedDescription,
    });

    setIsEditModalOpen(false);
  };

  const handleDelete = () => {
    if (window.confirm(`Tem certeza que deseja eliminar a equipa "${team.name}"?`)) {
      navigate('/nucleo/equipas');
    }
  };

  const handleAddMember = () => {
    if (selectedMemberId === null) {
      alert('Por favor, selecione um membro.');
      return;
    }

    setTeam({
      ...team,
      members: [...team.members, selectedMemberId],
    });

    setSelectedMemberId(null);
    setIsAddMemberModalOpen(false);
  };

  const handleRemoveMember = (memberId: number) => {
    if (window.confirm('Tem certeza que deseja remover este membro da equipa?')) {
      setTeam({
        ...team,
        members: team.members.filter((id) => id !== memberId),
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Team Info */}
            <div>
              {/* Team Avatar */}
              <div className="flex justify-center mb-8">
                <div className="w-48 h-48 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
                  <svg
                    className="w-24 h-24 text-gray-700"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                  </svg>
                </div>
              </div>

              {/* Team Details */}
              <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
                <div>
                  <label className="block text-teal-500 font-medium mb-2">
                    Nome
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {team.name}
                  </div>
                </div>

                <div>
                  <label className="block text-teal-500 font-medium mb-2">
                    Modalidade
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {team.modality}
                  </div>
                </div>

                <div>
                  <label className="block text-teal-500 font-medium mb-2">
                    Descrição
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800 min-h-[100px]">
                    {team.description}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 mt-6">
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

            {/* Right Column - Team Members */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Equipa</h2>
                <button
                  onClick={() => setIsAddMemberModalOpen(true)}
                  className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
                >
                  <span>+</span>
                  Adicionar Membro
                </button>
              </div>

              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {teamMembers.length > 0 ? (
                  teamMembers.map((member) => (
                    <div
                      key={member.id}
                      className="px-4 py-3 bg-gray-100 rounded-md flex justify-between items-center group"
                    >
                      <span className="text-gray-800 font-medium">{member.name}</span>
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium transition-colors opacity-0 group-hover:opacity-100"
                      >
                        Remover Membro
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-8">
                    Nenhum membro na equipa.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Team Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Equipa</h2>
            
            <div className="space-y-4">
              {/* Team Name */}
              <div>
                <label htmlFor="editName" className="block text-gray-700 font-medium mb-2">
                  Nome da Equipa <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="editName"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome da equipa"
                />
              </div>

              {/* Modality */}
              <div>
                <label htmlFor="editModality" className="block text-gray-700 font-medium mb-2">
                  Modalidade <span className="text-red-500">*</span>
                </label>
                <select
                  id="editModality"
                  value={editedModality}
                  onChange={(e) => setEditedModality(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Modalidade</option>
                  {modalities.map((modality) => (
                    <option key={modality} value={modality}>
                      {modality}
                    </option>
                  ))}
                </select>
              </div>

              {/* Description */}
              <div>
                <label htmlFor="editDescription" className="block text-gray-700 font-medium mb-2">
                  Descrição
                </label>
                <textarea
                  id="editDescription"
                  value={editedDescription}
                  onChange={(e) => setEditedDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[100px]"
                  placeholder="Digite a descrição da equipa"
                />
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsEditModalOpen(false);
                  setEditedName('');
                  setEditedModality('');
                  setEditedDescription('');
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

      {/* Add Member Modal */}
      {isAddMemberModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Membro</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="selectMember" className="block text-gray-700 font-medium mb-2">
                  Selecionar Membro <span className="text-red-500">*</span>
                </label>
                <select
                  id="selectMember"
                  value={selectedMemberId || ''}
                  onChange={(e) => setSelectedMemberId(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Membro</option>
                  {availableMembers.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
                {availableMembers.length === 0 && (
                  <p className="text-sm text-gray-500 mt-2">Todos os membros já estão na equipa.</p>
                )}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsAddMemberModalOpen(false);
                  setSelectedMemberId(null);
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddMember}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
                disabled={availableMembers.length === 0}
              >
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamDetail;
