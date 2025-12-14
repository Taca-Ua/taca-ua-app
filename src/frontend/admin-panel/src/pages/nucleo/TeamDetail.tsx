import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { teamsApi, type Team } from '../../api/teams';
// import { membersApi, type Student } from '../../api/members';
import { modalitiesApi, type Modality } from '../../api/modalities';

const TeamDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [team, setTeam] = useState<Team | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedModalityId, setEditedModalityId] = useState<number>(0);
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null);

  // Fetch team data, students, and modalities
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [teams, fetchedStudents, fetchedModalities] = await Promise.all([
          teamsApi.getAll(),
          studentsApi.getAll(),
          modalitiesApi.getAll(),
        ]);

        const foundTeam = teams.find(t => t.id === Number(id));

        if (!foundTeam) {
          setError('Equipa não encontrada');
          setTimeout(() => navigate('/nucleo/equipas'), 2000);
          return;
        }

        setTeam(foundTeam);
        setStudents(fetchedStudents);
        setModalities(fetchedModalities);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Erro ao carregar dados');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8">
          <div className="max-w-7xl mx-auto flex justify-center items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8">
          <div className="max-w-7xl mx-auto">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error || 'Equipa não encontrada'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const teamMembers = students.filter((student) => team.players.includes(student.id));
  const availableMembers = students.filter((student) => !team.players.includes(student.id));

  const getModalityName = (modalityId: number) => {
    const modality = modalities.find(m => m.id === modalityId);
    return modality ? modality.name : `Modalidade ${modalityId}`;
  };

  const handleEdit = () => {
    setEditedName(team.name);
    setEditedModalityId(team.modality_id);
    setIsEditModalOpen(true);
  };

  const handleSave = async () => {
    if (!editedName.trim()) {
      alert('Por favor, preencha o nome da equipa.');
      return;
    }

    if (!editedModalityId) {
      alert('Por favor, selecione uma modalidade.');
      return;
    }

    try {
      setError(null);
      // Update team name (modality cannot be changed according to API)
      await teamsApi.update(team.id, {
        name: editedName,
      });

      // Refresh team data
      const teams = await teamsApi.getAll();
      const updatedTeam = teams.find(t => t.id === team.id);
      if (updatedTeam) {
        setTeam(updatedTeam);
      }

      setIsEditModalOpen(false);
    } catch (err) {
      console.error('Error updating team:', err);
      setError('Erro ao atualizar equipa');
    }
  };

  const handleDelete = () => {
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    try {
      setError(null);
      await teamsApi.delete(team.id);
      navigate('/nucleo/equipas');
    } catch (err) {
      console.error('Error deleting team:', err);
      setError('Erro ao eliminar equipa');
      setDeleteConfirmOpen(false);
    }
  };

  const handleAddMember = async () => {
    if (selectedMemberId === null) {
      alert('Por favor, selecione um membro.');
      return;
    }

    try {
      setError(null);
      await teamsApi.update(team.id, {
        players_add: [selectedMemberId],
      });

      // Refresh team data
      const teams = await teamsApi.getAll();
      const updatedTeam = teams.find(t => t.id === team.id);
      if (updatedTeam) {
        setTeam(updatedTeam);
      }

      setSelectedMemberId(null);
      setIsAddMemberModalOpen(false);
    } catch (err) {
      console.error('Error adding member:', err);
      setError('Erro ao adicionar membro');
    }
  };

  const handleRemoveMember = async (memberId: number) => {
    if (!window.confirm('Tem certeza que deseja remover este membro da equipa?')) {
      return;
    }

    try {
      setError(null);
      await teamsApi.update(team.id, {
        players_remove: [memberId],
      });

      // Refresh team data
      const teams = await teamsApi.getAll();
      const updatedTeam = teams.find(t => t.id === team.id);
      if (updatedTeam) {
        setTeam(updatedTeam);
      }
    } catch (err) {
      console.error('Error removing member:', err);
      setError('Erro ao remover membro');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Error Banner */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

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
                    {getModalityName(team.modality_id)}
                  </div>
                </div>

                <div>
                  <label className="block text-teal-500 font-medium mb-2">
                    Número de Jogadores
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {team.players.length}
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
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-800 font-medium">{member.full_name}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            member.member_type === 'technical_staff'
                              ? 'bg-purple-100 text-purple-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {member.member_type === 'technical_staff' ? 'Equipa Técnica' : 'Estudante'}
                          </span>
                        </div>
                        <span className="text-gray-500 text-sm">{member.student_number}</span>
                      </div>
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium transition-colors opacity-0 group-hover:opacity-100"
                      >
                        Remover
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

              {/* Modality (read-only) */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Modalidade
                </label>
                <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                  {getModalityName(editedModalityId)}
                </div>
                <p className="text-sm text-gray-500 mt-1">A modalidade não pode ser alterada</p>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsEditModalOpen(false);
                  setEditedName('');
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
                      {member.full_name} ({member.student_number})
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

      {/* Delete Confirmation Modal */}
      {deleteConfirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Confirmar Eliminação</h2>
            <p className="text-gray-600 mb-6">
              Tem certeza que deseja eliminar a equipa <strong>{team.name}</strong>?
              Esta ação não pode ser desfeita.
            </p>

            <div className="flex gap-4">
              <button
                onClick={() => setDeleteConfirmOpen(false)}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={confirmDelete}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamDetail;
