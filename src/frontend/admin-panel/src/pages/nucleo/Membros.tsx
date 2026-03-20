import { useState, useEffect } from 'react';
import HelpTooltip from '../../components/HelpTooltip';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import {
  studentsApi,
  staffApi,
  type Student,
  type Staff,
} from '../../api/members';
import { coursesApi, type Course } from '../../api/courses';
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';

type CombinedMember =
  | { memberType: 'participant'; data: Student }
  | { memberType: 'staff'; data: Staff };


function Membros() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [memberName, setMemberName] = useState('');
  const [memberType, setMemberType] = useState<'participant' | 'staff'>('participant');
  const [courseId, setCourseId] = useState('');
  const [studentNumber, setStudentNumber] = useState('');
  const [identifierType, setIdentifierType] = useState<'contact' | 'staff_number'>('contact');
  const [contact, setContact] = useState('');
  const [staffNumber, setStaffNumber] = useState('');

  const [members, setMembers] = useState<CombinedMember[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [filterType, setFilterType] = useState<'all' | 'participant' | 'staff'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all members from both APIs
  useEffect(() => {
    const fetchMembers = async () => {
      try {
        setLoading(true);

        const [participants, staff] = await Promise.all([
          studentsApi.getAll(),
          staffApi.getAll()
        ]);

        // Combine and tag members
        const unifiedMembers: CombinedMember[] = [
          ...participants.map(p => ({ data: p, memberType: 'participant' as const })),
          ...staff.map(s => ({ data: s, memberType: 'staff' as const }))
        ];

        setMembers(unifiedMembers);
      } catch (err) {
        console.error('Failed to fetch members:', err);
        notify('Não foi possível carregar os membros do núcleo. Tente recarregar a página.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, []);

  // Fetch courses on mount
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const data = await coursesApi.getAll();
        setCourses(data);
      } catch (err) {
        console.error('Failed to fetch courses:', err);
      }
    };

    fetchCourses();
  }, []);

  // Filter members based on type and search query
  const filteredMembers = members
    .filter(member => {
      const matchesType = filterType === 'all' || member.memberType === filterType;
      const matchesSearch = (member.data.full_name).toLowerCase().includes(searchQuery.toLowerCase());
      return matchesType && matchesSearch;
    })
    .sort((a, b) => a.data.full_name.localeCompare(b.data.full_name));

  const handleAddMember = async () => {
    // Validation: Name is required
    if (!memberName.trim()) {
      notify('Por favor, preencha o nome.', 'error');
      return;
    }

    try {
      if (memberType === 'participant') {
        // Validate participant fields
        const trimmedStudentNumber = studentNumber.trim();

        if (!trimmedStudentNumber) {
          notify('Por favor, preencha o número de estudante.', 'error');
          return;
        }

        if (!/^\d+$/.test(trimmedStudentNumber)) {
          notify('O número de estudante (NMEC) deve conter apenas dígitos.', 'error');
          return;
        }

        if (trimmedStudentNumber.length > 13) {
          notify('O número de estudante (NMEC) não pode ter mais de 13 caracteres.', 'error');
          return;
        }

        if (!courseId.trim()) {
          notify('Por favor, preencha o curso.', 'error');
          return;
        }

        const newParticipant = await studentsApi.create({
          full_name: memberName,
          course_id: String(courseId),
          student_number: trimmedStudentNumber,
          is_member: true,
        });

        // Add to local state
        setMembers([...members, { data: newParticipant, memberType: 'participant' }]);
      } else {
        // Validate staff fields - need either contact or staff_number
        const staffData: { full_name: string; contact?: string; staff_number?: string } = {
          full_name: memberName,
        };

        if (identifierType === 'contact') {
          const trimmedContact = contact.trim();

          if (!trimmedContact) {
            notify('Por favor, preencha o contacto.', 'error');
            return;
          }

          if (!/^\+?\d+$/.test(trimmedContact)) {
            notify('O contacto (telemóvel) deve conter apenas dígitos e pode ter um "+" no início.', 'error');
            return;
          }

          if (trimmedContact.length > 13) {
            notify('O contacto (telemóvel) não pode ter mais de 13 caracteres.', 'error');
            return;
          }

          staffData.contact = trimmedContact;
        } else {
          const trimmedStaffNumber = staffNumber.trim();

          if (!trimmedStaffNumber) {
            notify('Por favor, preencha o número de staff.', 'error');
            return;
          }

          if (!/^\d+$/.test(trimmedStaffNumber)) {
            notify('O número de staff deve conter apenas dígitos.', 'error');
            return;
          }

          if (trimmedStaffNumber.length > 13) {
            notify('O número de staff não pode ter mais de 13 caracteres.', 'error');
            return;
          }

          staffData.staff_number = trimmedStaffNumber;
        }

        const newStaff = await staffApi.create(staffData);

        // Add to local state
        setMembers([...members, { data: newStaff, memberType: 'staff' }]);
      }

      // Reset form
      setMemberName('');
      setMemberType('participant');
      setCourseId('');
      setStudentNumber('');
      setContact('');
      setStaffNumber('');
      setIdentifierType('contact');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create member:', err);
      notify('Não foi possível adicionar o membro. O número de estudante ou contacto podem já estar em uso.', 'error');
    }
  };

  const handleMemberClick = (member: CombinedMember) => {
    navigate(`/nucleo/membros/${member.memberType}/${member.data.id}`);
  };

  const getDisplayInfo = (member: CombinedMember): string => {
    if (member.memberType === 'participant') {
      return `NMEC: ${member.data.student_number}`;
    } else {
      if ('contact' in member.data && member.data.contact) {
        return `Tel: ${member.data.contact}`;
      }
      if ('staff_number' in member.data && member.data.staff_number) {
        return `Staff: ${member.data.staff_number}`;
      }
      return 'N/A';
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <div className="flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Pesquisar por nome..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="sm:w-48">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as 'all' | 'participant' | 'staff')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="all">Todos</option>
                  <option value="participant">Participantes</option>
                  <option value="staff">Staff</option>
                </select>
              </div>

              <button
                onClick={() => setIsModalOpen(true)}
                className={`${btn.primary} px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2 justify-center sm:justify-start focus:outline-none focus:ring-2 focus:ring-teal-500`}
              >
                <span>+</span>
                Adicionar Membro
              </button>
            </div>
          </div>

          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {!loading && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold mb-6 text-gray-800">
                Membros
                <span className="text-gray-500 text-lg ml-2">({filteredMembers.length})</span>
              </h2>

              {filteredMembers.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">Nenhum membro encontrado</p>
                  <p className="text-sm mt-2">Tente ajustar os filtros ou adicionar novos membros</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {filteredMembers.map((member) => (
                    <button
                      type="button"
                      key={`${member.memberType}-${member.data.id}`}
                      onClick={() => handleMemberClick(member)}
                      className="w-full text-left bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <span className="text-gray-800 font-medium">{member.data.full_name}</span>
                          <span className="text-xs px-2 py-1 rounded-full bg-teal-100 text-teal-700 font-medium">
                            {member.memberType === 'participant' ? 'Participante' : 'Staff'}
                          </span>
                        </div>
                        <span className="text-gray-600 text-sm">
                          {getDisplayInfo(member)}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Membro</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="memberName" className="block text-gray-700 font-medium mb-2">
                  Nome <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="memberName"
                  value={memberName}
                  onChange={(e) => setMemberName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome do membro"
                />
              </div>

              <div>
                <label htmlFor="memberType" className="block text-gray-700 font-medium mb-2">
                  Tipo <HelpTooltip text="Participante: estudante que compete nas provas desportivas. Staff: pessoal de apoio (treinadores, dirigentes) sem competição direta." className="ml-1" /> <span className="text-red-500">*</span>
                </label>
                <select
                  id="memberType"
                  value={memberType}
                  onChange={(e) => setMemberType(e.target.value as 'participant' | 'staff')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="participant">Participante</option>
                  <option value="staff">Staff</option>
                </select>
              </div>

              {memberType === 'participant' && (
                <>
                  <div>
                    <label htmlFor="studentNumber" className="block text-gray-700 font-medium mb-2">
                      Número de Estudante <HelpTooltip text="Número mecanológráfico (NMEC) do estudante na Universidade de Aveiro. Utilizado para verificação de elegibilidade." className="ml-1" /> <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="studentNumber"
                      value={studentNumber}
                      onChange={(e) => setStudentNumber(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o NMEC (ex: 12345)"
                    />
                  </div>
                  <div>
                    <label htmlFor="courseId" className="block text-gray-700 font-medium mb-2">
                      Curso <HelpTooltip text="Curso académico do estudante na Universidade de Aveiro. Utilizado para organização e filtros de equipas." className="ml-1" /> <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="courseId"
                      value={courseId}
                      onChange={(e) => setCourseId(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">Selecionar Curso</option>
                      {[...courses].sort((a, b) => a.name.localeCompare(b.name)).map((course) => (
                        <option key={course.id} value={course.id}>
                          {course.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {memberType === 'staff' && (
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Identificação <HelpTooltip text="Escolha como identificar o colaborador: por contacto telefónico ou número de staff. Pelo menos um é obrigatório para o registo." className="ml-1" /> <span className="text-red-500">*</span>
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
                        value="staff_number"
                        checked={identifierType === 'staff_number'}
                        onChange={() => setIdentifierType('staff_number')}
                        className="mr-2"
                      />
                      <span className="text-gray-700">Nº Staff</span>
                    </label>
                  </div>

                  {identifierType === 'contact' ? (
                    <input
                      type="tel"
                      value={contact}
                      onChange={(e) => setContact(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o contacto (ex: 912345678)"
                    />
                  ) : (
                    <input
                      type="text"
                      value={staffNumber}
                      onChange={(e) => setStaffNumber(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o número de staff"
                    />
                  )}
                </div>
              )}
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setMemberName('');
                  setMemberType('participant');
                  setCourseId('');
                  setStudentNumber('');
                  setContact('');
                  setStaffNumber('');
                  setIdentifierType('contact');
                }}
                className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
              >
                Cancelar
              </button>
              <button
                onClick={handleAddMember}
                className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500`}
              >
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Membros;
