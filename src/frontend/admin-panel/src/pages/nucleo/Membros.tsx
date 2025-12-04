import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { studentsApi } from '../../api/students';
import type { Student } from '../../api/students';

interface Member {
  id: number;
  name: string;
  role: 'jogador' | 'tecnico';
  contact?: string;
  nmec?: string;
}

function Membros() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [memberName, setMemberName] = useState('');
  const [memberRole, setMemberRole] = useState<'jogador' | 'tecnico'>('jogador');
  const [identifierType, setIdentifierType] = useState<'contact' | 'nmec'>('contact');
  const [contact, setContact] = useState('');
  const [nmec, setNmec] = useState('');
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch students from API
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        setError(null);
        const students = await studentsApi.getAll();

        // Transform Student[] to Member[]
        const transformedMembers: Member[] = students.map((student: Student) => ({
          id: student.id,
          name: student.full_name,
          role: student.member_type === 'technical_staff' ? 'tecnico' : 'jogador',
          nmec: student.student_number,
        }));

        setMembers(transformedMembers);
      } catch (err) {
        console.error('Failed to fetch students:', err);
        setError('Erro ao carregar membros. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, []);

  const jogadores = members.filter(m => m.role === 'jogador');
  const tecnicos = members.filter(m => m.role === 'tecnico');

  const handleAddMember = async () => {
    // Validation: Name is required
    if (!memberName.trim()) {
      alert('Por favor, preencha o nome.');
      return;
    }

    // Validation: Need either contact or NMEC depending on role
    let identifier = '';
    if (memberRole === 'jogador') {
      // Jogadores must have NMEC
      if (!nmec.trim()) {
        alert('Por favor, preencha o NMEC.');
        return;
      }
      identifier = nmec;
    } else {
      // Técnicos can have either contact or NMEC
      if (identifierType === 'contact') {
        if (!contact.trim()) {
          alert('Por favor, preencha o contacto.');
          return;
        }
        identifier = contact;
      } else {
        if (!nmec.trim()) {
          alert('Por favor, preencha o NMEC.');
          return;
        }
        identifier = nmec;
      }
    }

    try {
      const newStudent = await studentsApi.create({
        full_name: memberName,
        student_number: identifier, // Use whichever identifier was provided
        is_member: true,
        member_type: memberRole === 'jogador' ? 'student' : 'technical_staff',
        // email is optional, not sending it
      });

      // Add to local state
      const newMember: Member = {
        id: newStudent.id,
        name: newStudent.full_name,
        role: memberRole,
        // Store in the appropriate field for display
        ...(memberRole === 'jogador' || identifierType === 'nmec'
          ? { nmec: identifier }
          : { contact: identifier }
        ),
      };
      setMembers([...members, newMember]);

      // Reset form
      setMemberName('');
      setMemberRole('jogador');
      setContact('');
      setNmec('');
      setIdentifierType('contact');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create student:', err);
      alert('Erro ao adicionar membro. Por favor, tente novamente.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header with Add Button */}
          <div className="flex justify-end mb-6">
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-teal-500 hover:bg-teal-600 text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Membros
            </button>
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
            <>
              {/* Jogadores Section */}
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Jogadores</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {jogadores.map((jogador) => (
                <div
                  key={jogador.id}
                  onClick={() => navigate(`/nucleo/membros/${jogador.id}`)}
                  className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-800 font-medium">{jogador.name}</span>
                    <span className="text-gray-600 text-sm">
                      {jogador.contact ? `Tel: ${jogador.contact}` : `NMEC: ${jogador.nmec}`}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

              {/* Equipa Técnica Section */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Equipa Técnica</h2>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {tecnicos.map((tecnico) => (
                    <div
                      key={tecnico.id}
                      onClick={() => navigate(`/nucleo/membros/${tecnico.id}`)}
                      className="bg-gray-100 p-4 rounded-md hover:bg-gray-200 transition-colors cursor-pointer"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-gray-800 font-medium">{tecnico.name}</span>
                        <span className="text-gray-600 text-sm">
                          {tecnico.contact ? `Tel: ${tecnico.contact}` : `NMEC: ${tecnico.nmec}`}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
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
                  Nome
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

              {/* Role Select */}
              <div>
                <label htmlFor="memberRole" className="block text-gray-700 font-medium mb-2">
                  Tipo
                </label>
                <select
                  id="memberRole"
                  value={memberRole}
                  onChange={(e) => setMemberRole(e.target.value as 'jogador' | 'tecnico')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="jogador">Jogador</option>
                  <option value="tecnico">Técnico</option>
                </select>
              </div>

              {/* Identifier Type Selection - Only for Técnicos */}
              {memberRole === 'tecnico' && (
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
                      value={contact}
                      onChange={(e) => setContact(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o contacto (ex: 912345678)"
                    />
                  ) : (
                    <input
                      type="text"
                      value={nmec}
                      onChange={(e) => setNmec(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="Digite o NMEC (ex: 12345)"
                    />
                  )}
                </div>
              )}

              {/* NMEC Input - Required for Jogadores */}
              {memberRole === 'jogador' && (
                <div>
                  <label htmlFor="nmecJogador" className="block text-gray-700 font-medium mb-2">
                    NMEC <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="nmecJogador"
                    value={nmec}
                    onChange={(e) => setNmec(e.target.value)}
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
                  setMemberName('');
                  setMemberRole('jogador');
                  setContact('');
                  setNmec('');
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
