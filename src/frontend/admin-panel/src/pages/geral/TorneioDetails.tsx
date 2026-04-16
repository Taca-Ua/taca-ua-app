import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentDetail } from '../../api/tournaments';
import { btn } from '../../styles/buttonStyles';
import TournamentInfoComponent from '../../components/tournaments/TournamentInfoComponent';
import TournamentCompetitorsComponent from '../../components/tournaments/TournamentCompetitorsComponent';
import MatchesListComponent from '../../components/matches/MatchesListComponent';

// Main component
const TorneioDetails = () => {
  const tournamentId = useParams<{ id: string }>().id;
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [tournament, setTournament] = useState<TournamentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();

  // Determine where to navigate back to
  const fromModalityId = searchParams.get('fromModality');
  const handleBack = () => {
    if (fromModalityId) {
      navigate(`/geral/modalidades/${fromModalityId}`);
    } else {
      navigate('/geral/torneios');
    }
  };

  useEffect(() => {
    const loadTournament = async () => {
      if (!tournamentId) return;

      try {
        setLoading(true);
        const data = await tournamentsApi.getById(tournamentId);
        setTournament(data);
      } catch (err) {
        console.error('Failed to fetch tournament:', err);
        notify('Não foi possível carregar os dados do torneio. Tente recarregar a página.', 'error');
        handleBack();
      } finally {
        setLoading(false);
      }
    };

    loadTournament();
  }, [tournamentId]);

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        </div>
      </div>
    );
  }

  if (!tournament) return null;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Torneio</h1>
            <button
              onClick={handleBack}
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
            >
              Voltar
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TournamentInfoComponent tournamentState={[tournament, setTournament]} />

            <div>
              <TournamentCompetitorsComponent tournamentState={[tournament, setTournament]}/>
            </div>
          </div>

          <div className="mt-6">
            <MatchesListComponent tournament={tournament} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TorneioDetails;
