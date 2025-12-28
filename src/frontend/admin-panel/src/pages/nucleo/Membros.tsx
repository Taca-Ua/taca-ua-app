import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import {
  participantsApi,
  staffApi,
  type UnifiedMember,
} from '../../api/members';
import { coursesApi, type Course } from '../../api/courses';

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

  const [members, setMembers] = useState<UnifiedMember[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'participant' | 'staff'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all members from both APIs
  useEffect(() => {
    const fetchMembers = async () => {
      try {
        setLoading(true);
        setError(null);

        const [participants, staff] = await Promise.all([
          participantsApi.getAll(),
          staffApi.getAll()
        ]);

        // Combine and tag members
        const unifiedMembers: UnifiedMember[] = [
          ...participants.map(p => ({ ...p, memberType: 'participant' as const })),
          ...staff.map(s => ({ ...s, memberType: 'staff' as const }))
        ];

        setMembers(unifiedMembers);
      } catch (err) {
        console.error('Failed to fetch members:', err);
        setError('Erro ao carregar membros. Por favor, tente novamente.');
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
  const filteredMembers = members.filter(member => {
    const matchesType = filterType === 'all' || member.memberType === filterType;
    const matchesSearch = member.full_name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const handleAddMember = async () => {
    // Validation: Name is required
    if (!memberName.trim()) {
      alert('Por favor, preencha o nome.');
      return;
    }

    try {
      if (memberType === 'participant') {
        // Validate participant fields
        if (!studentNumber.trim()) {
          alert('Por favor, preencha o número de estudante.');
          return;
        }
        if (!courseId.trim()) {
          alert('Por favor, preencha o curso.');
          return;
        }

        const newParticipant = await participantsApi.create({
          full_name: memberName,
          course_id: String(courseId),
          student_number: studentNumber,
          is_member: true,
        });

        // Add to local state
        setMembers([...members, { ...newParticipant, memberType: 'participant' }]);
      } else {
        // Validate staff fields - need either contact or staff_number
        const staffData: { full_name: string; contact?: string; staff_number?: string } = {
          full_name: memberName,
        };

        if (identifierType === 'contact') {
          if (!contact.trim()) {
            alert('Por favor, preencha o contacto.');
            return;
          }
          staffData.contact = contact;
        } else {
          if (!staffNumber.trim()) {
            alert('Por favor, preencha o número de staff.');
            return;
          }
          staffData.staff_number = staffNumber;
        }

        const newStaff = await staffApi.create(staffData);

        // Add to local state
        setMembers([...members, { ...newStaff, memberType: 'staff' }]);
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
      alert('Erro ao adicionar membro. Por favor, tente novamente.');
    }
  };

  const handleMemberClick = (member: UnifiedMember) => {
    navigate(`/nucleo/membros/${member.memberType}/${member.id}`);
  };

  const getDisplayInfo = (member: UnifiedMember): string => {
    if (member.memberType === 'participant') {
      return `NMEC: ${member.student_number}`;
    } else {
      if ('contact' in member && member.contact) {
        return `Tel: ${member.contact}`;
      }
      if ('staff_number' in member && member.staff_number) {
        return `Staff: ${member.staff_number}`;
      }
      return 'N/A';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header with Filters and Add Button */}
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              {/* Search Bar */}
              <div className="flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Pesquisar por nome..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              {/* Type Filter */}
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

              {/* Add Button */}
              <button
                onClick={() => setIsModalOpen(true)}
                className="bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2 justify-center sm:justify-start"
              >
                <span>+</span>
                Adicionar Membro
              </button>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}

          {/* Content - Only show when not loading */}
          {!loading && !error && (
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
                    <div
                      key={`${member.memberType}-${member.id}`}
                      onClick={() => handleMemberClick(member)}
                      className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <span className="text-gray-800 font-medium">{member.full_name}</span>
                          <span className="text-xs px-2 py-1 rounded-full bg-teal-100 text-teal-700 font-medium">
                            {member.memberType === 'participant' ? 'Participante' : 'Staff'}
                          </span>
                        </div>
                        <span className="text-gray-600 text-sm">
                          {getDisplayInfo(member)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Add Member Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Membro</h2>

            <div className="space-y-4">
              {/* Name Input */}
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

              {/* Type Select */}
              <div>
                <label htmlFor="memberType" className="block text-gray-700 font-medium mb-2">
                  Tipo <span className="text-red-500">*</span>
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

              {/* Participant Fields */}
              {memberType === 'participant' && (
                <>
                  <div>
                    <label htmlFor="studentNumber" className="block text-gray-700 font-medium mb-2">
                      Número de Estudante <span className="text-red-500">*</span>
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
                      Curso <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="courseId"
                      value={courseId}
                      onChange={(e) => setCourseId(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                    >
                      <option value="">Selecionar Curso</option>
                      {courses.map((course) => (
                        <option key={course.id} value={course.id}>
                          {course.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {/* Staff Fields */}
              {memberType === 'staff' && (
                <div>
                  <label className="block text-gray-700 font-medium mb-2">
                    Identificação <span className="text-red-500">*</span>
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

                  {/* Contact or Staff Number Input */}
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

            {/* Modal Actions */}
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
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddMember}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
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
