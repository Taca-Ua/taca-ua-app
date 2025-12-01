import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';

interface Match {
  id: number;
  team1: string;
  team2: string;
  date: string;
  time: string;
  location: string;
  modality: string;
  team1Members: number[];
  team2Members: number[];
}

interface Member {
  id: number;
  name: string;
}

const MatchDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [match, setMatch] = useState<Match | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedTeam1Members, setSelectedTeam1Members] = useState<number[]>([]);
  const [selectedTeam2Members, setSelectedTeam2Members] = useState<number[]>([]);
  const [editingTeam, setEditingTeam] = useState<'team1' | 'team2'>('team1');

  // Mock data for matches
  const mockMatches: Match[] = [
    {
      id: 1,
      team1: 'Equipa 1',
      team2: 'Equipa 4',
      date: '2025-12-05',
      time: '14:00',
      location: 'Campo Principal',
      modality: 'Futebol',
      team1Members: [1, 2, 3, 4, 5],
      team2Members: [6, 7, 8, 9],
    },
    {
      id: 2,
      team1: 'Equipa 2',
      team2: 'Equipa 8',
      date: '2025-12-03',
      time: '16:00',
      location: 'Pavilhão A',
      modality: 'Basquetebol',
      team1Members: [2, 4, 6, 8],
      team2Members: [1, 3, 5, 7, 9],
    },
    {
      id: 3,
      team1: 'Equipa 3',
      team2: 'Equipa 9',
      date: '2025-11-28',
      time: '18:00',
      location: 'Pavilhão B',
      modality: 'Voleibol',
      team1Members: [1, 3, 5, 7],
      team2Members: [2, 4, 6, 8, 9],
    },
    {
      id: 4,
      team1: 'Equipa 5',
      team2: 'Equipa 4',
      date: '2025-12-10',
      time: '15:30',
      location: 'Pavilhão C',
      modality: 'Futsal',
      team1Members: [1, 2, 3, 4, 5],
      team2Members: [6, 7, 8],
    },
    {
      id: 5,
      team1: 'Equipa 6',
      team2: 'Equipa 7',
      date: '2025-11-25',
      time: '17:00',
      location: 'Campo Secundário',
      modality: 'Andebol',
      team1Members: [3, 4, 5, 6],
      team2Members: [1, 2, 7, 8, 9],
    },
    {
      id: 6,
      team1: 'Equipa 1',
      team2: 'Equipa 2',
      date: '2025-12-15',
      time: '19:00',
      location: 'Estádio Central',
      modality: 'Rugby',
      team1Members: [1, 2, 3, 4, 5, 6, 7, 8, 9],
      team2Members: [2, 4, 6, 8],
    },
    {
      id: 7,
      team1: 'Equipa 7',
      team2: 'Equipa 8',
      date: '2025-12-12',
      time: '16:30',
      location: 'Pavilhão B',
      modality: 'Basquetebol',
      team1Members: [5, 6, 7],
      team2Members: [1, 8, 9],
    },
    {
      id: 8,
      team1: 'Equipa 3',
      team2: 'Equipa 6',
      date: '2025-12-08',
      time: '18:30',
      location: 'Campo Secundário',
      modality: 'Futebol',
      team1Members: [1, 3, 5, 7, 9],
      team2Members: [2, 4, 6, 8],
    },
    {
      id: 9,
      team1: 'Equipa 5',
      team2: 'Equipa 9',
      date: '2025-12-20',
      time: '20:00',
      location: 'Pavilhão A',
      modality: 'Voleibol',
      team1Members: [1, 2, 3, 4],
      team2Members: [5, 6, 7, 8, 9],
    },
  ];

  // Mock data for members
  const mockMembers: Member[] = [
    { id: 1, name: 'Membro 1' },
    { id: 2, name: 'Membro 2' },
    { id: 3, name: 'Membro 3' },
    { id: 4, name: 'Membro 4' },
    { id: 5, name: 'Membro 5' },
    { id: 6, name: 'Membro 6' },
    { id: 7, name: 'Membro 7' },
    { id: 8, name: 'Membro 8' },
    { id: 9, name: 'Membro 9' },
    { id: 10, name: 'Membro 10' },
  ];

  useEffect(() => {
    const foundMatch = mockMatches.find((m) => m.id === Number(id));
    if (foundMatch) {
      setMatch(foundMatch);
      setSelectedTeam1Members(foundMatch.team1Members);
      setSelectedTeam2Members(foundMatch.team2Members);
    } else {
      navigate('/nucleo/jogos');
    }
  }, [id, navigate]);

  if (!match) {
    return null;
  }

  // Combine all team members for the match - use current state values
  const allMatchMembers = [
    ...selectedTeam1Members,
    ...selectedTeam2Members
  ];
  const matchMembers = mockMembers.filter((member) => 
    allMatchMembers.includes(member.id)
  );

  const handleSaveTeamMembers = () => {
    if (match) {
      // Update the match with new team members
      setMatch({
        ...match,
        team1Members: selectedTeam1Members,
        team2Members: selectedTeam2Members,
      });
      setIsEditModalOpen(false);
      // Here you would also make an API call to save the changes
    }
  };

  const toggleTeamMember = (memberId: number) => {
    if (editingTeam === 'team1') {
      if (selectedTeam1Members.includes(memberId)) {
        setSelectedTeam1Members(selectedTeam1Members.filter(id => id !== memberId));
      } else {
        setSelectedTeam1Members([...selectedTeam1Members, memberId]);
      }
    } else {
      if (selectedTeam2Members.includes(memberId)) {
        setSelectedTeam2Members(selectedTeam2Members.filter(id => id !== memberId));
      } else {
        setSelectedTeam2Members([...selectedTeam2Members, memberId]);
      }
    }
  };

  const handleOpenEditModal = (team: 'team1' | 'team2') => {
    setEditingTeam(team);
    setIsEditModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Match Details */}
            <div className="bg-white rounded-lg shadow-md p-8">
              {/* Team Avatars */}
              <div className="flex justify-center items-center gap-8 mb-8">
                {/* Team 1 Avatar */}
                <div className="w-32 h-32 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
                  <svg
                    className="w-16 h-16 text-gray-700"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                  </svg>
                </div>

                {/* VS Text */}
                <div className="text-3xl font-bold text-gray-700">
                  VS
                </div>

                {/* Team 2 Avatar */}
                <div className="w-32 h-32 bg-indigo-100 rounded-full flex items-center justify-center shadow-lg">
                  <svg
                    className="w-16 h-16 text-gray-700"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                  </svg>
                </div>
              </div>

              {/* Match Details Section */}
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-6">Detalhes do jogo</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Equipa 1
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.team1}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Equipa 2
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.team2}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Modalidade
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.modality}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Data
                    </label>
                    <div className="text-gray-800 font-medium">
                      {new Date(match.date).toLocaleDateString('pt-PT')}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Hora
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.time}
                    </div>
                  </div>

                  <div>
                    <label className="block text-gray-600 text-sm mb-1">
                      Local
                    </label>
                    <div className="text-gray-800 font-medium">
                      {match.location}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Team Members */}
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-xl font-bold text-gray-800 mb-6">Membros da Equipa</h2>

              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {matchMembers.length > 0 ? (
                  matchMembers.map((member) => (
                    <div
                      key={member.id}
                      className="px-4 py-3 bg-gray-100 rounded-md"
                    >
                      <span className="text-gray-800 font-medium">{member.name}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-8">
                    Nenhum membro associado a este jogo.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <button
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              onClick={() => handleOpenEditModal('team1')}
            >
              Editar {match.team1}
            </button>
            <button
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              onClick={() => handleOpenEditModal('team2')}
            >
              Editar {match.team2}
            </button>
            <button
              className="px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-md font-medium transition-colors"
              onClick={() => alert('Imprimir Ficha de Jogo')}
            >
              Imprimir Ficha de Jogo
            </button>
          </div>
        </div>
      </div>

      {/* Edit Team Members Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 animate-slideUp max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">
              Editar {editingTeam === 'team1' ? match.team1 : match.team2}
            </h2>
            
            <div>
              <div className="space-y-2 max-h-[500px] overflow-y-auto">
                {mockMembers.map((member) => (
                  <label
                    key={`${editingTeam}-${member.id}`}
                    className="flex items-center gap-3 px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-md cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={
                        editingTeam === 'team1'
                          ? selectedTeam1Members.includes(member.id)
                          : selectedTeam2Members.includes(member.id)
                      }
                      onChange={() => toggleTeamMember(member.id)}
                      className="w-5 h-5 text-teal-500 rounded focus:ring-2 focus:ring-teal-500"
                    />
                    <span className="text-gray-800">{member.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsEditModalOpen(false);
                  // Reset selections to original values
                  if (match) {
                    setSelectedTeam1Members(match.team1Members);
                    setSelectedTeam2Members(match.team2Members);
                  }
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveTeamMembers}
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
};

export default MatchDetail;
