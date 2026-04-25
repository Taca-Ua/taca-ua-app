import { useParams } from 'react-router-dom';
import TeamDetailComponent from '../../components/teams/TeamDetailComponent';
import Button from '../../components/utils/Button';

const TeamDetailPage = () => {
  const teamId = useParams<{ id: string }>().id || "";

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes da Equipa</h1>
            <div>
              <Button
                onClick={() => window.history.back()}
                type='secondary'
                padding='px-6 py-3'
              >
                Voltar
              </Button>
            </div>
          </div>

          <TeamDetailComponent
            teamId={teamId}
          />
        </div>
      </div>
  );
};

export default TeamDetailPage;
