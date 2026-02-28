import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { studentsApi, type StudentDetail } from '../api';

function Students() {
  const [students, setStudents] = useState<StudentDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [memberFilter, setMemberFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = {
          page,
          page_size: 20,
          ...(debouncedSearch && { search: debouncedSearch }),
          ...(memberFilter !== 'all' && { is_member: memberFilter === 'member' }),
        };

        const data = await studentsApi.getAll(params);
        setStudents(data.items);
        setTotalPages(Math.ceil(data.total / data.page_size));
      } catch (err) {
        console.error('Error fetching students:', err);
        setError('Erro ao carregar estudantes. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, [page, debouncedSearch, memberFilter]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Estudantes
            </h1>
            <p className="text-lg text-gray-600">
              Veja todos os estudantes participantes da Taça UA
            </p>
          </div>

          {/* Filters */}
          <div className="mb-6 flex gap-4 flex-wrap">
            <input
              type="text"
              placeholder="Pesquisar por nome ou número..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 min-w-[250px] px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
            <select
              value={memberFilter}
              onChange={(e) => {
                setMemberFilter(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="all">Todos</option>
              <option value="member">Apenas Membros</option>
              <option value="non-member">Não Membros</option>
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar estudantes...</p>
            </div>
          ) : (
            <>
              {/* Students Table */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          Número
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          Nome
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          Curso
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          Núcleo
                        </th>
                        <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                          Membro
                        </th>
                        <th className="px-6 py-4 text-center text-sm font-semibold text-gray-700">
                          Equipas
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {students.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                            {debouncedSearch
                              ? 'Nenhum estudante encontrado com os filtros selecionados.'
                              : 'Não há estudantes disponíveis.'}
                          </td>
                        </tr>
                      ) : (
                        students.map((student) => (
                          <tr key={student.student_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4">
                              <span className="font-mono text-sm text-gray-700">
                                {student.student_number}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <p className="font-medium text-gray-800">{student.full_name}</p>
                            </td>
                            <td className="px-6 py-4">
                              <p className="text-gray-700">{student.course_name}</p>
                              <p className="text-xs text-gray-500">{student.course_abbreviation}</p>
                            </td>
                            <td className="px-6 py-4">
                              <p className="text-gray-700">{student.nucleo_name}</p>
                              <p className="text-xs text-gray-500">{student.nucleo_abbreviation}</p>
                            </td>
                            <td className="px-6 py-4 text-center">
                              {student.is_member ? (
                                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                                  Sim
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold">
                                  Não
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="text-gray-700 font-medium">
                                {student.team_count}
                              </span>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex justify-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <span className="px-4 py-2 text-gray-700">
                    Página {page} de {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Próxima
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default Students;
