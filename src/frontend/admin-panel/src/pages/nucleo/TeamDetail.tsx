import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import HelpTooltip from '../../components/HelpTooltip';
import { teamsApi, type TeamDetail } from '../../api/teams';
import { studentsApi, type Student } from '../../api/members';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';

const TeamDetailsEditModal = ({
  team,
  setTeam,
  onClose,
} : {
  team: TeamDetail;
  setTeam: React.Dispatch<React.SetStateAction<TeamDetail | undefined>>;
  onClose: () => void;
}) => {
  const [editedName, setEditedName] = useState(team.name);
  const { notify } = useNotification();

  const handleSave = async () => {
    if (!editedName.trim()) {
      notify('Por favor, preencha o nome da equipa.', 'error');
      return;
    }

    try {
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
      notify('Não foi possível guardar as alterações à equipa. Tente novamente.', 'error');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Editar Equipa</h2>

        <div className="space-y-4">
          <div>
            <label htmlFor="editName" className="block text-gray-700 font-medium mb-2">
              Nome da Equipa <HelpTooltip text="Nome pelo qual a equipa é identificada nos torneios e rankings. Deve ser único dentro do núcleo." className="ml-1" /> <span className="text-red-500">*</span>
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

        <div className="flex gap-4 mt-6">
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium transition-colors`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
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
  team: TeamDetail;
  setTeam: React.Dispatch<React.SetStateAction<TeamDetail | undefined>>;
  onClose: () => void;
}) => {
  const [availableParticipants, setAvailableParticipants] = useState<Student[]>([]);
  const [editedParticipantsList, setEditedParticipantsList] = useState<Student[]>(team.players);
  const [searchQuery, setSearchQuery] = useState('');

  const originalParticipantsList = [...team.players];

  // Fetch all participants for that course
  useEffect(() => {
    const fetchParticipants = async () => {
      try {
        const participantsData = await studentsApi.getAll({
          course_id: team.course.id,
        });
        setAvailableParticipants(participantsData);
      } catch (err) {
        console.error('Error fetching participants:', err);
      }
    };

    fetchParticipants();
  }, []);

  const handleSave = async () => {
    const playersToAdd = editedParticipantsList
      .filter(ep => !originalParticipantsList.some(op => op.id === ep.id))
      .map(p => p.id);

    const playersToRemove = originalParticipantsList
      .filter(op => !editedParticipantsList.some(ep => ep.id === op.id))
      .map(p => p.id);

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

  const toggleParticipant = (participant: Student) => {
    const isSelected = editedParticipantsList.some(p => p.id === participant.id);
    if (isSelected) {
      setEditedParticipantsList(editedParticipantsList.filter(p => p.id !== participant.id));
    } else {
      setEditedParticipantsList([...editedParticipantsList, participant]);
    }
  };

  const filteredParticipants = availableParticipants.filter(p =>
    p.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.student_number.includes(searchQuery)
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-white rounded-lg p-8 max-w-lg w-full mx-4 animate-slideUp max-h-[90vh] flex flex-col">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Gerir Membros da Equipa</h2>

        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Pesquisar por nome ou NMEC..."
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 mb-4"
        />

        <div className="flex-1 overflow-y-auto space-y-2 mb-3 max-h-96">
          {filteredParticipants.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              {availableParticipants.length === 0 ? 'Nenhum participante disponível' : 'Nenhum resultado para a pesquisa'}
            </p>
          ) : (
            filteredParticipants.map(participant => {
              const isSelected = editedParticipantsList.some(p => p.id === participant.id);
              return (
                <div
                  key={participant.id}
                  onClick={() => toggleParticipant(participant)}
                  className={`flex items-center justify-between px-4 py-3 rounded-md cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-teal-50 border border-teal-300 hover:bg-teal-100'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 ${
                      isSelected ? 'bg-teal-500 text-white' : 'bg-gray-200 text-gray-600'
                    }`}>
                      {participant.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{participant.full_name}</p>
                      <p className="text-sm text-gray-500">NMEC: {participant.student_number}</p>
                    </div>
                  </div>
                  {isSelected ? (
                    <svg className="w-5 h-5 text-teal-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  )}
                </div>
              );
            })
          )}
        </div>

        <p className="text-sm text-gray-500 mb-4">
          {editedParticipantsList.length} participante(s) selecionado(s)
        </p>

        <div className="flex gap-4 flex-shrink-0">
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium transition-colors`}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors`}
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

const TeamDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [team, setTeam] = useState<TeamDetail>();
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // Fetch team data, participants, modalities, and courses
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        const [teamData] = await Promise.all([
          teamsApi.get(id!),
        ]);

        const foundTeam = teamData;

        if (!foundTeam) {
          notify('Equipa não encontrada', 'error');
          setTimeout(() => navigate('/nucleo/equipas'), 2000);
          return;
        }

        setTeam(foundTeam);
      } catch (err) {
        console.error('Error fetching data:', err);
        notify('Não foi possível carregar os dados da equipa. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="flex-1 p-8">
          <div className="max-w-7xl mx-auto flex justify-center items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!team) {
    return null;
  }

  const handleEdit = () => {
    setIsEditModalOpen(true);
  };

  const handleDelete = () => {
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    try {
      await teamsApi.delete(team.id);
      navigate('/nucleo/equipas');
    } catch (err) {
      console.error('Error deleting team:', err);
      notify('Não foi possível eliminar a equipa. Poderá ter jogos associados.', 'error');
      setDeleteConfirmOpen(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    try {
      const newTeam = await teamsApi.update(team.id, {
        players_remove: [memberId],
      });
      setTeam(newTeam);
    } catch (err) {
      console.error('Error removing member from team:', err);
      notify('Não foi possível remover o membro da equipa. Tente novamente.', 'error');
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes da Equipa</h1>
            <button
              onClick={() => navigate('/nucleo/equipas')}
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
            >
              Voltar
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
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
                    Modalidade <HelpTooltip text="Desporto desta equipa. Define os torneios em que pode participar." className="ml-1" />
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {team.modality.name}
                  </div>
                </div>

                <div>
                  <label className="block text-teal-500 font-medium mb-2">
                    Curso <HelpTooltip text="Curso académico que esta equipa representa." className="ml-1" />
                  </label>
                  <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                    {team.course.name}
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

                <div className="flex gap-4 mt-6">
                  <button
                    onClick={handleEdit}
                    className={`flex-1 px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors`}
                  >
                    Editar
                  </button>
                  <button
                    onClick={handleDelete}
                    className={`flex-1 px-6 py-3 ${btn.danger} rounded-md font-medium transition-colors`}
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Equipa</h2>
                <button
                  onClick={() => setIsAddMemberModalOpen(true)}
                  className={`px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2`}
                >
                  <span>+</span>
                  Adicionar Membro
                </button>
              </div>

              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {team.players.length > 0 ? (
                  team.players.map((member: Student) => (
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
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className={`px-3 py-1 ${btn.danger}Ghost rounded-md text-sm font-medium transition-colors`}
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

      {isEditModalOpen && (
        <TeamDetailsEditModal
          team={team}
          setTeam={setTeam}
          onClose={() => setIsEditModalOpen(false)}
        />
      )}

      {isAddMemberModalOpen && (
        <TeamParticipantsEdditModal
          team={team}
          setTeam={setTeam}
          onClose={() => setIsAddMemberModalOpen(false)}
        />
      )}

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
                className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium transition-colors`}
              >
                Cancelar
              </button>
              <button
                onClick={confirmDelete}
                className={`flex-1 px-4 py-2 ${btn.danger} rounded-md font-medium transition-colors`}
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

export default TeamDetailPage;
