import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { teamsApi, type TeamDetail } from '../api';

function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [team, setTeam] = useState<TeamDetail | null>(null);
  const [members, setMembers] = useState<TeamDetail['players'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const [teamData] = await Promise.all([
          teamsApi.getById(id),
        ]);
        setTeam(teamData);
        setMembers(teamData.players);
      } catch (err) {
        console.error('Failed to load team:', err);
        setError('Erro ao carregar equipa.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-4xl mx-auto">
          {/* Breadcrumb */}
          <div className="mb-6 flex items-center gap-2 text-sm text-gray-500">
            <Link to="/equipas" className="hover:text-teal-600">
              Equipas
            </Link>
            <span>/</span>
            <span className="text-gray-700">{team?.team_name ?? 'Detalhe'}</span>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
              <p className="mt-4 text-gray-600">A carregar equipa...</p>
            </div>
          ) : team ? (
            <>
              {/* Team info card */}
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
                  {team.team_name}
                </h1>
                <p className="text-teal-600 font-medium text-lg mb-5">
                  {team.modality_name || team.modality_type_name}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Núcleo</p>
                    <p className="font-medium text-gray-700">{team.nucleo_name}</p>
                    <p className="text-xs text-gray-500">{team.nucleo_abbreviation}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Curso</p>
                    <p className="font-medium text-gray-700">{team.course_name}</p>
                    <p className="text-xs text-gray-500">{team.course_abbreviation}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Jogadores</p>
                    <p className="text-2xl font-bold text-teal-600">{team.player_count}</p>
                  </div>
                </div>
              </div>

              {/* Members list */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                  <h2 className="text-lg font-semibold text-gray-800">
                    Jogadores ({members?.length || 0})
                  </h2>
                </div>

                {(!members || members.length === 0) ? (
                  <div className="p-8 text-center">
                    <p className="text-gray-500">Nenhum jogador registado nesta equipa.</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {members.map((member) => (
                      <div
                        key={member.student_id}
                        className="px-6 py-4 flex items-center justify-between"
                      >
                        <div>
                          <p className="font-medium text-gray-800">{member.full_name}</p>
                          <p className="text-sm text-gray-500">
                            {member.student_number}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Back link */}
              <div className="mt-6">
                <Link to="/equipas" className="text-teal-600 hover:text-teal-700 text-sm font-medium">
                  ← Voltar às Equipas
                </Link>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Equipa não encontrada.</p>
              <Link to="/equipas" className="text-teal-600 hover:text-teal-700 mt-4 inline-block">
                Voltar às Equipas
              </Link>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default TeamDetailPage;
