import { useState } from 'react';
import { type TeamListItem } from '../../api/teams';
import TeamsListComponent from '../../components/teams/TeamsListComponent';
import TeamsCreateModal from '../../components/teams/TeamsCreateModal';
import Button from '../../components/utils/Button';

const Equipas = () => {
  const createTeamController = useState(false);

  const [teams, setTeams] = useState<TeamListItem[]>([]);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Equipas</h1>
            <Button
              onClick={() => createTeamController[1](true)}
              type='primary'
            >
              + Adicionar Equipa
            </Button>
          </div>

          <TeamsListComponent
            teamsState={[teams, setTeams]}
          />
        </div>
        <TeamsCreateModal
          controller={createTeamController}
          onCreate={(newTeam) => setTeams([...teams, newTeam])}
        />
      </div>
  );
};

export default Equipas;
