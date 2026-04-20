import { useState } from 'react';
import { type TeamListItem } from '../../api/teams';
import { btn } from '../../styles/buttonStyles';
import TeamsListComponent from '../../components/teams/TeamsListComponent';
import TeamsCreateModel from '../../components/teams/TeamsCreateModel';

const Equipas = () => {
  const createTeamController = useState(false);

  const [teams, setTeams] = useState<TeamListItem[]>([]);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Equipas</h1>
            <button
              onClick={() => createTeamController[1](true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2`}
            >
              <span>+</span>
              Adicionar Equipa
            </button>
          </div>

          <TeamsListComponent
            teamsState={[teams, setTeams]}
          />
        </div>
        <TeamsCreateModel
          controller={createTeamController}
          onCreate={(newTeam) => setTeams([...teams, newTeam])}
        />
      </div>
  );
};

export default Equipas;
