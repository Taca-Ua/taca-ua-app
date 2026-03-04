import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from "../../components/geral_navbar";
import { modalitiesApi } from '../../api/modalities';
import { teamsApi } from '../../api/teams';
import { tournamentsApi } from '../../api/tournaments';
import { seasonsApi, type Season } from '../../api/seasons';
import { nucleosApi } from '../../api/nucleos';
import { useAuth } from '../../hooks/useAuth';

function DashboardGeral() {
  const navigate = useNavigate();
  // username is used in the welcome greeting below
  const { username } = useAuth();
  const [stats, setStats] = useState({
    modalities: 0,
    courses: 0,
    tournaments: 0,
    activeTournaments: 0,
    teams: 0,
  });
  const [loading, setLoading] = useState(true);
  const [currentSeason, setCurrentSeason] = useState<Season | null>(null);
  const [draftSeason, setDraftSeason] = useState<Season | null>(null);
  const [showStartModal, setShowStartModal] = useState(false);
  const [showFinishModal, setShowFinishModal] = useState(false);
  const [seasonLoading, setSeasonLoading] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);

        // Fetch all data in parallel
        const [modalities, tournaments, teams, seasons, nucleos] = await Promise.all([
          modalitiesApi.getAll(),
          tournamentsApi.getAll(),
          teamsApi.getAll(), // Get teams from all courses
          seasonsApi.getAll(),
          nucleosApi.getAll(),
        ]);

        // Count active tournaments
        const activeTournaments = tournaments.filter(t => t.status === 'active').length;

        // Find current active season and draft season
        const active = seasons.find(s => s.status === 'active') || null;
        const draft = seasons.find(s => s.status === 'draft') || null;

        setCurrentSeason(active);
        setDraftSeason(draft);

        setStats({
          modalities: modalities.length,
          courses: nucleos.length,
          tournaments: tournaments.length,
          activeTournaments,
          teams: teams.length,
        });
      } catch (err) {
        console.error('Failed to fetch dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleStartSeason = async () => {
    if (!draftSeason) return;

    try {
      setSeasonLoading(true);
      await seasonsApi.start(draftSeason.id);

      // Refresh seasons
      const seasons = await seasonsApi.getAll();
      const active = seasons.find(s => s.status === 'active') || null;
      const draft = seasons.find(s => s.status === 'draft') || null;

      setCurrentSeason(active);
      setDraftSeason(draft);
      setShowStartModal(false);

      alert('Época iniciada com sucesso!');
    } catch (err) {
      console.error('Failed to start season:', err);
      alert('Erro ao iniciar época');
    } finally {
      setSeasonLoading(false);
    }
  };

  const handleFinishSeason = async () => {
    if (!currentSeason) return;

    try {
      setSeasonLoading(true);
      await seasonsApi.finish(currentSeason.id);

      // Refresh seasons
      const seasons = await seasonsApi.getAll();
      const active = seasons.find(s => s.status === 'active') || null;
      const draft = seasons.find(s => s.status === 'draft') || null;

      setCurrentSeason(active);
      setDraftSeason(draft);
      setShowFinishModal(false);

      alert('Época finalizada com sucesso!');
    } catch (err) {
      console.error('Failed to finish season:', err);
      alert('Erro ao finalizar época');
    } finally {
      setSeasonLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Geral</h1>
          <p className="text-gray-600 mb-8">
            Bem-vindo, <span className="font-semibold">{username ?? 'Administrador'}</span>
          </p>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          ) : (
            <>
              <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-lg shadow-lg p-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="text-4xl">🗓️</div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold mb-2 text-gray-800">Gestão de Época</h2>
                    {currentSeason ? (
                      <div>
                        <p className="text-lg mb-4">
                          <span className="font-semibold">Época Atual:</span>{' '}
                          <span className="text-green-700 font-bold">{currentSeason.year}</span>{' '}
                          <span className="inline-block px-3 py-1 bg-green-500 text-white rounded-full text-sm ml-2">
                            ATIVA
                          </span>
                        </p>
                        <button
                          onClick={() => setShowFinishModal(true)}
                          className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-bold transition-colors"
                        >
                          🏁 Finalizar Época {currentSeason.year}
                        </button>
                        <p className="text-sm text-gray-600 mt-2">
                          ⚠️ Esta ação irá encerrar a época atual e não pode ser revertida!
                        </p>
                      </div>
                    ) : draftSeason ? (
                      <div>
                        <p className="text-lg mb-4">
                          <span className="font-semibold">Nenhuma época ativa.</span><br />
                          <span className="text-orange-700">Época {draftSeason.year} está em rascunho.</span>
                        </p>
                        <button
                          onClick={() => setShowStartModal(true)}
                          className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-md font-bold transition-colors"
                        >
                          ▶️ Iniciar Época {draftSeason.year}
                        </button>
                        <p className="text-sm text-gray-600 mt-2">
                          ⚠️ Certifique-se de que tudo está configurado antes de iniciar a época!
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-lg mb-4 text-red-700 font-semibold">
                          ⚠️ Nenhuma época disponível! Crie uma nova época primeiro.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div
                  onClick={() => navigate('/geral/modalidades')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Modalidades</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.modalities}</p>
                  <p className="text-sm text-gray-500 mt-2">Modalidades registadas</p>
                </div>

                <div
                  onClick={() => navigate('/geral/torneios')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-purple-600">Torneios</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.tournaments}</p>
                  <p className="text-sm text-gray-500 mt-2">Total de torneios</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-2 text-orange-600">Torneios Ativos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.activeTournaments}</p>
                  <p className="text-sm text-gray-500 mt-2">Em andamento</p>
                </div>

                <div
                  onClick={() => navigate('/geral/nucleos')}
                  className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h2 className="text-xl font-semibold mb-2 text-teal-600">Núcleos</h2>
                  <p className="text-3xl font-bold text-gray-800">{stats.courses}</p>
                  <p className="text-sm text-gray-500 mt-2">Núcleos ativos</p>
                </div>
              </div>

            </>
          )}
        </div>
      </div>

      {showStartModal && draftSeason && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">⚠️ Confirmar Início de Época</h2>
            <div className="mb-6 space-y-3">
              <p className="text-gray-700">
                Tem certeza que deseja <span className="font-bold">iniciar a época {draftSeason.year}</span>?
              </p>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <p className="text-sm text-yellow-800 font-semibold mb-2">ATENÇÃO:</p>
                <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
                  <li>Esta ação irá marcar a época como <strong>ATIVA</strong></li>
                  <li>Apenas uma época pode estar ativa de cada vez</li>
                  <li>Se houver uma época ativa, ela será automaticamente finalizada</li>
                  <li>Certifique-se de que todas as configurações estão corretas</li>
                </ul>
              </div>
              <p className="text-sm text-gray-600 italic mt-4">
                Digite "INICIAR" para confirmar:
              </p>
              <input
                type="text"
                className="border border-gray-300 rounded-md px-4 py-2 w-full"
                placeholder="Digite INICIAR"
                id="confirm-start-input"
              />
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setShowStartModal(false)}
                disabled={seasonLoading}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-md font-medium disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  const input = document.getElementById('confirm-start-input') as HTMLInputElement;
                  if (input?.value === 'INICIAR') {
                    handleStartSeason();
                  } else {
                    alert('Por favor, digite "INICIAR" para confirmar');
                  }
                }}
                disabled={seasonLoading}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-bold disabled:opacity-50"
              >
                {seasonLoading ? 'A iniciar...' : 'Iniciar Época'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showFinishModal && currentSeason && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">⚠️ Confirmar Finalização de Época</h2>
            <div className="mb-6 space-y-3">
              <p className="text-gray-700">
                Tem certeza que deseja <span className="font-bold text-red-600">finalizar a época {currentSeason.year}</span>?
              </p>
              <div className="bg-red-50 border-l-4 border-red-500 p-4">
                <p className="text-sm text-red-800 font-semibold mb-2">⚠️ ATENÇÃO - AÇÃO IRREVERSÍVEL:</p>
                <ul className="text-sm text-red-700 space-y-1 list-disc list-inside">
                  <li><strong>Esta ação NÃO pode ser revertida!</strong></li>
                  <li>A época será marcada como <strong>FINALIZADA</strong></li>
                  <li>Não será possível modificar jogos ou torneios desta época</li>
                  <li>Os resultados serão permanentemente arquivados</li>
                  <li>Verifique que todos os jogos foram concluídos</li>
                </ul>
              </div>
              <p className="text-sm text-gray-600 italic mt-4">
                Digite "FINALIZAR" para confirmar:
              </p>
              <input
                type="text"
                className="border border-gray-300 rounded-md px-4 py-2 w-full"
                placeholder="Digite FINALIZAR"
                id="confirm-finish-input"
              />
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setShowFinishModal(false)}
                disabled={seasonLoading}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-md font-medium disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  const input = document.getElementById('confirm-finish-input') as HTMLInputElement;
                  if (input?.value === 'FINALIZAR') {
                    handleFinishSeason();
                  } else {
                    alert('Por favor, digite "FINALIZAR" para confirmar');
                  }
                }}
                disabled={seasonLoading}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-bold disabled:opacity-50"
              >
                {seasonLoading ? 'A finalizar...' : 'Finalizar Época'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardGeral;
