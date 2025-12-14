import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import NucleoSidebar from '../../components/nucleo_navbar';
import { participantsApi, staffApi, type Participant, type Staff } from '../../api/members';

type MemberType = 'participant' | 'staff';
type Member = Participant | Staff;

function MemberDetail() {
  const { type, id } = useParams<{ type: MemberType; id: string }>();
  const navigate = useNavigate();
  const [member, setMember] = useState<Member | null>(null);
  const [memberType, setMemberType] = useState<MemberType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editedName, setEditedName] = useState('');
  const [editedContact, setEditedContact] = useState('');
  const [isMember, setIsMember] = useState(true);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // Fetch member data
  useEffect(() => {
    const fetchMember = async () => {
      try {
        setLoading(true);
        setError(null);

		console.log('Fetching member with ID:', id, 'and type:', type);

        if (!id || !type) {
          setError('ID ou tipo inválido');
          setTimeout(() => navigate('/nucleo/membros'), 2000);
          return;
        }

        if (type !== 'participant' && type !== 'staff') {
          setError('Tipo de membro inválido');
          setTimeout(() => navigate('/nucleo/membros'), 2000);
          return;
        }

        setMemberType(type);

        if (type === 'participant') {
          const participant = await participantsApi.getById(id as any);
          setMember(participant);
        } else {
          const staff = await staffApi.getById(id as any);
          setMember(staff);
        }
      } catch (err) {
        console.error('Error fetching member:', err);
        setError('Erro ao carregar os dados do membro');
        setTimeout(() => navigate('/nucleo/membros'), 2000);
      } finally {
        setLoading(false);
      }
    };

    fetchMember();
  }, [id, type, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8">
          <div className="max-w-3xl mx-auto flex justify-center items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !member) {
    return (
      <div className="min-h-screen bg-gray-50">
        <NucleoSidebar />
        <div className="p-8">
          <div className="max-w-3xl mx-auto">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error || 'Membro não encontrado'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleEdit = () => {
    if (!member) return;
    setEditedName(member.full_name);

    if (memberType === 'participant') {
      setIsMember((member as Participant).is_member);
    } else if (memberType === 'staff') {
      setEditedContact((member as Staff).contact || '');
    }

    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!member || !editedName.trim() || !memberType) return;

    try {
      setError(null);

      if (memberType === 'participant') {
        const updatedMember = await participantsApi.update(member.id as any, {
          full_name: editedName,
          is_member: isMember,
        });
        setMember(updatedMember);
      } else if (memberType === 'staff') {
        const updatedMember = await staffApi.update(member.id as any, {
          full_name: editedName,
          contact: editedContact || undefined,
        });
        setMember(updatedMember);
      }

      setIsModalOpen(false);
    } catch (err) {
      console.error('Error updating member:', err);
      setError('Erro ao atualizar o membro');
    }
  };

  const handleDelete = () => {
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!member || !memberType) return;

    try {
      setError(null);

      if (memberType === 'participant') {
        await participantsApi.delete(member.id as any);
      } else if (memberType === 'staff') {
        await staffApi.delete(member.id as any);
      }

      navigate('/nucleo/membros');
    } catch (err) {
      console.error('Error deleting member:', err);
      setError('Erro ao eliminar o membro');
      setDeleteConfirmOpen(false);
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
              {/* Type Badge */}
              <div>
                <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${
                  memberType === 'participant'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-purple-100 text-purple-700'
                }`}>
                  {memberType === 'participant' ? 'Participante' : 'Equipa Técnica'}
                </span>
              </div>

              {/* Name */}
              <div>
                <label className="block text-teal-500 font-medium mb-2">
                  Nome
                </label>
                <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                  {member.full_name}
                </div>
              </div>

              {/* Participant-specific fields */}
              {memberType === 'participant' && (
                <>
                  {/* Student Number */}
                  <div>
                    <label className="block text-teal-500 font-medium mb-2">
                      Número de Estudante
                    </label>
                    <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                      {(member as Participant).student_number}
                    </div>
                  </div>

                  {/* Member Status */}
                  <div>
                    <label className="block text-teal-500 font-medium mb-2">
                      Estado de Membro
                    </label>
                    <div className="w-full px-4 py-3 bg-gray-100 rounded-md">
                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                        (member as Participant).is_member
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {(member as Participant).is_member ? 'Membro' : 'Não-Membro'}
                      </span>
                    </div>
                  </div>

                  {/* Course ID */}
                  <div>
                    <label className="block text-teal-500 font-medium mb-2">
                      Curso
                    </label>
                    <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                      {(member as Participant).course_id}
                    </div>
                  </div>
                </>
              )}

              {/* Staff-specific fields */}
              {memberType === 'staff' && (
                <>
                  {/* Staff Number */}
                  {(member as Staff).staff_number && (
                    <div>
                      <label className="block text-teal-500 font-medium mb-2">
                        Número de Staff
                      </label>
                      <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                        {(member as Staff).staff_number}
                      </div>
                    </div>
                  )}

                  {/* Contact */}
                  {(member as Staff).contact && (
                    <div>
                      <label className="block text-teal-500 font-medium mb-2">
                        Contacto
                      </label>
                      <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
                        {(member as Staff).contact}
                      </div>
                    </div>
                  )}
                </>
              )}
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
                  Nome <span className="text-red-500">*</span>
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

              {/* Participant-specific fields */}
              {memberType === 'participant' && (
                <>
                  {/* Student Number (read-only) */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">
                      Número de Estudante
                    </label>
                    <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                      {(member as Participant).student_number}
                    </div>
                  </div>

                  {/* Is Member Toggle */}
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">
                      Tipo
                    </label>
                    <div className="flex gap-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="isMember"
                          checked={isMember}
                          onChange={() => setIsMember(true)}
                          className="mr-2"
                        />
                        <span className="text-gray-700">Membro</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="isMember"
                          checked={!isMember}
                          onChange={() => setIsMember(false)}
                          className="mr-2"
                        />
                        <span className="text-gray-700">Não-Membro</span>
                      </label>
                    </div>
                  </div>
                </>
              )}

              {/* Staff-specific fields */}
              {memberType === 'staff' && (
                <>
                  {/* Staff Number (read-only) */}
                  {(member as Staff).staff_number && (
                    <div>
                      <label className="block text-gray-700 font-medium mb-2">
                        Número de Staff
                      </label>
                      <div className="w-full px-4 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600">
                        {(member as Staff).staff_number}
                      </div>
                    </div>
                  )}

                  {/* Contact Input */}
                  <div>
                    <label htmlFor="editContact" className="block text-gray-700 font-medium mb-2">
                      Contacto
                    </label>
                    <input
                      type="text"
                      id="editContact"
                      value={editedContact}
                      onChange={(e) => setEditedContact(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o contacto"
                    />
                  </div>
                </>
              )}
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setEditedName('');
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

      {/* Delete Confirmation Modal */}
      {deleteConfirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Confirmar Eliminação</h2>
            <p className="text-gray-600 mb-6">
              Tem certeza que deseja eliminar <strong>{member.full_name}</strong>?
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
}

export default MemberDetail;
