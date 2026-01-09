import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { teamsApi, type Team, type Player } from '../../api/teams';
import { participantsApi, type Participant } from '../../api/members';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { coursesApi, type Course } from '../../api/courses';

const TeamDetailsEditModal = ({
  team,
  setTeam,
  onClose,
} : {
  team: Team;
  setTeam: React.Dispatch<React.SetStateAction<Team | undefined>>;
  onClose: () => void;
}) => {
  const [editedName, setEditedName] = useState(team.name);

  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    if (!editedName.trim()) {
      alert('Por favor, preencha o nome da equipa.');
      return;
    }

    try {
      setError(null);
      const teamData = await teamsApi.update(team.id, {
        name: editedName,
      });

      // Refresh team data
      if (teamData) {
        setTeam(teamData);
      }

      onClose();
    } catch (err) {
      console.error('Error updating team:', err);
      setError('Erro ao atualizar equipa');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Equipa</h2>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

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
        </div>

        {/* Modal Actions */}
        <div className="flex gap-4 mt-6">
          <button
            onClick={onClose}
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
  );
};

const TeamParticipantsEdditModal = ({
  team,
  setTeam,
  onClose,
} : {
  team: Team;
  setTeam: React.Dispatch<React.SetStateAction<Team | undefined>>;
  onClose: () => void;
}) => {
  const [availableParticipants, setAvailableParticipants] = useState<Player[]>([]);
  const [originalParticipantsList, setOriginalParticipantsList] = useState<Player[]>(team.players);
  const [editedParticipantsList, setEditedParticipantsList] = useState<Player[]>(team.players);

  // Fetch all participants for that course
  useEffect(() => {
    const fetchParticipants = async () => {
      try {
        const participantsData = await participantsApi.getAll(team.course_id);
        setAvailableParticipants(participantsData);
      } catch (err) {
        console.error('Error fetching participants:', err);
      }
    };

    fetchParticipants();
  }, []);

  const handleSave = async () => {
    console.log('Original Participants:', originalParticipantsList);
    console.log('Edited Participants:', editedParticipantsList);

    // Logic to save added participants to the team
    const playersToAdd = editedParticipantsList
      .filter(ep => !originalParticipantsList.some(op => op.id === ep.id))
      .map(p => p.id);

    const playersToRemove = originalParticipantsList
      .filter(op => !editedParticipantsList.some(ep => ep.id === op.id))
      .map(p => p.id);

    console.log('Players to add:', playersToAdd);
    console.log('Players to remove:', playersToRemove);

    try {
      const newTeam = await teamsApi.update(team.id, {
        players_add: playersToAdd,
        players_remove: playersToRemove,
      });
      setTeam(newTeam);
    } catch (err) {
      console.error('Error updating team participants:', err);
    }

    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Membro</h2>

        <div className="space-y-4">
          <div>
            <label htmlFor="selectMember" className="block text-gray-700 font-medium mb-2">
              Selecionar Membros <span className="text-red-500">*</span>
            </label>
            <select
              id="selectMember"
              onChange={(e) => {
                const selectedId = e.target.value;
                const selectedParticipant = availableParticipants.find(p => p.id === selectedId);
                console.log('Selected Participant:', availableParticipants);
                if (selectedParticipant) {
                  setEditedParticipantsList([...editedParticipantsList, selectedParticipant]);
                }
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="">-- Selecionar Membro --</option>
              {availableParticipants.map(participant => (
                <option
                  key={participant.id}
                  value={participant.id}
                  disabled={editedParticipantsList.some(p => p.id === participant.id)}
                >
                  {participant.full_name} (Nº {participant.student_number})
                </option>
              ))}
            </select>

            {availableParticipants.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">Todos os membros já estão na equipa.</p>
            )}
          </div>
        </div>

        {/* Modal Actions */}
        <div className="flex gap-4 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
          >
            Adicionar
          </button>
        </div>
      </div>
    </div>
  );
};

const TeamDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [team, setTeam] = useState<Team>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // Fetch team data, participants, modalities, and courses
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [teamData] = await Promise.all([
          teamsApi.get(id!),
        ]);

        const foundTeam = teamData;

        if (!foundTeam) {
          setError('Equipa não encontrada');
          setTimeout(() => navigate('/nucleo/equipas'), 2000);
          return;
        }

        setTeam(foundTeam);
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

  const handleEdit = () => {
    setIsEditModalOpen(true);
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

  const handleRemoveMember = async (memberId: string) => {
    try {
      setError(null);
      const newTeam = await teamsApi.update(team.id, {
        players_remove: [memberId],
      });
      setTeam(newTeam);
    } catch (err) {
      console.error('Error removing member from team:', err);
      setError('Erro ao remover membro da equipa');
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
                    {team.modality_name}
                  </div>
                </div>

                <div>
                  <label className="block text-teal-500 font-medium mb-2">
                    Curso
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {team.course_name}
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
                {team.players.length > 0 ? (
                  team.players.map((member: Player) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                          <span className="text-teal-700 font-medium">
                            {member.full_name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-gray-800 font-medium">{member.full_name}</p>
                          {/* <p className="text-sm text-gray-500">Nº {member.student_number}</p> */}
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded-md text-sm font-medium transition-colors"
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
        <TeamDetailsEditModal
          team={team}
          setTeam={setTeam}
          onClose={() => setIsEditModalOpen(false)}
        />
      )}

      {/* Add Member Modal */}
      {isAddMemberModalOpen && (
        <TeamParticipantsEdditModal
          team={team}
          setTeam={setTeam}
          onClose={() => setIsAddMemberModalOpen(false)}
        />
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
