import { useParams, useNavigate } from 'react-router-dom';
import { btn } from '../../styles/buttonStyles';
import TeamDetailComponent from '../../components/teams/TeamDetailComponent';

const TeamDetailPage = () => {
  const teamId = useParams<{ id: string }>().id || "";
  const navigate = useNavigate();

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes da Equipa</h1>
            <button
              onClick={() => navigate('/nucleo/equipas')}
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
            >
              Voltar
            </button>
          </div>

          <TeamDetailComponent
            teamId={teamId}
          />
        </div>
      </div>
  );
};

export default TeamDetailPage;
