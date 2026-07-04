import { useNavigate, useParams } from 'react-router-dom';
import TeamInfoComponent from '../../components/teams/TeamInfoComponent';
import Button from '../../components/utils/Button';
import { navigateBack } from '../../utils';
import { teamsApi, type TeamDetail } from '../../api/teams';
import { useEffect, useState } from 'react';
import { useNotification } from '../../contexts/NotificationProvider';
import TabSystem from '../../components/TabSystem';
import MatchesCalendarComponent from '../../components/matches/MatchesCalendarComponent';
import TournamentListComponent from '../../components/tournaments/TournamentList';


const TeamDetailPage = () => {
  const teamId = useParams<{ id: string }>().id || "";
  const navigate = useNavigate();
  const { notify } = useNotification();

  const [team, setTeam] = useState<TeamDetail | null>(null);

  useEffect(() => {
    teamsApi.get(teamId)
      .then((data) => setTeam(data))
      .catch((error) => {
        console.error("Error fetching team data:", error);
        setTeam(null);
        notify("Erro ao carregar os detalhes da equipa.", "error");
      });
  }, [teamId]);

  const handleBack = () => {
    navigateBack(navigate, '/equipas');
  };

  return (
      <div className="flex-1 p-8 space-y-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes da Equipa</h1>
            <div>
              <Button
                onClick={handleBack}
                type='secondary'
                padding='px-6 py-3'
              >
                Voltar
              </Button>
            </div>
          </div>

          <TeamInfoComponent
            teamState={[team, setTeam]}
          />
        </div>

        <TabSystem
          elements={[
            { id: 'tournaments', label: 'Torneios', content: <TournamentListComponent teamId={teamId} /> },
            { id: 'matches', label: 'Jogos', content: <MatchesCalendarComponent teamId={teamId} /> },
          ]}
        />
      </div>
  );
};

export default TeamDetailPage;
