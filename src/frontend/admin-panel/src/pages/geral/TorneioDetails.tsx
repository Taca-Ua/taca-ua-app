import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useNotification } from '../../contexts/NotificationProvider';
import { tournamentsApi, type TournamentDetail } from '../../api/tournaments';
import { type MatchListItem } from '../../api/matches';
import TournamentInfoComponent from '../../components/tournaments/TournamentInfoComponent';
import TournamentCompetitorsComponent from '../../components/tournaments/TournamentCompetitorsComponent';
import MatchesListComponent from '../../components/matches/MatchesListComponent';
import MatchCreateModal from '../../components/matches/MatchCreateModal';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import { useAuth } from '../../hooks/useAuth';
import { navigateBack } from '../../utils';
import TornLeagueDisplayComponent from '../../components/tournaments/formats/league/TornLeagueDisplayComponent';
import GeneralFormatMatchesSuggestionsModal from '../../components/tournaments/formats/GeneralFormatMatchesSuggestionsModal';

// Main component
const TorneioDetails = () => {
  const tournamentId = useParams<{ id: string }>().id;
  const navigate = useNavigate();
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();

  const [tournament, setTournament] = useState<TournamentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const { notify } = useNotification();
  const [matches, setMatches] = useState<MatchListItem[]>([]);

  // Determine where to navigate back to
  const handleBack = () => {
    navigateBack(navigate, '/torneios');
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
      <div className="flex-1 flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (!tournament) return null;

  return (
      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">{tournament.name}</h1>
            <Button
              onClick={handleBack}
              type='secondary'
              padding='px-6 py-3'
            >
              Voltar
            </Button>
          </div>

          {/* Tournament Details */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TournamentInfoComponent tournamentState={[tournament, setTournament]} onDelete={handleBack} />

            <div>
              <TournamentCompetitorsComponent tournamentState={[tournament, setTournament]}/>
            </div>
          </div>

          {/* Format Details */}
          { (isAdminGeneral && tournament.format !== 'free') && (
            <div className="mt-6">
              <TornLeagueDisplayComponent
                tournamentState={[tournament, setTournament]}
              />
            </div>
          )}

          {/* Matches Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mt-6 flex flex-col gap-6">
            {tournament.format === 'free'? (
              <Button
                onClick={() => pushModal(
                  <MatchCreateModal
                    tournament={tournament}
                    onCreated={(newMatch) => {
                      setMatches((prev) => [...prev, newMatch]);
                    }}
                  />
                )}
                active={isAdminGeneral && tournament.competitors.length >= 2}
                flexible={true}
              >
                + Criar Jogo
              </Button>
            ) : (
              <Button
                onClick={() => pushModal(
                  <GeneralFormatMatchesSuggestionsModal format={tournament.format} tournamentId={tournament.id} />
                )}
                active={isAdminGeneral}
                flexible={true}
              >
                + Gerar Jogos
              </Button>
            )}
            <MatchesListComponent tournamentId={tournament.id} matchesState={[matches, setMatches]} />
          </div>
        </div>
      </div>
  );
};

export default TorneioDetails;
