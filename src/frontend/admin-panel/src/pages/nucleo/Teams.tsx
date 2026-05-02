import { useEffect, useState } from 'react';
import { teamsApi, type TeamListItem } from '../../api/teams';
import TeamsListComponent from '../../components/teams/TeamsListComponent';
import TeamsCreateModal from '../../components/teams/TeamsCreateModal';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import { useSeason } from '../../contexts/SeasonContext';

const Equipas = () => {
  const { pushModal } = useModal();
  const { loadedSeason } = useSeason();

  const [teams, setTeams] = useState<TeamListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    teamsApi.getAll({
      season_id: loadedSeason?.id,
    })
      .then((data) => setTeams(data))
      .catch((error) => {
        console.error('Erro ao carregar equipas:', error);
        setTeams([]);
      })
      .finally(() => setLoading(false));
  }, [loadedSeason?.id]);

  if (loading) {
    return <div className="text-gray-500">Carregando equipas...</div>;
  }

  if (!teams) {
    return <div className="text-red-500">Erro ao carregar equipas.</div>;
  }

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Equipas</h1>
            <Button
              onClick={() => pushModal(
                <TeamsCreateModal
                  onCreate={(newTeam) => setTeams([...teams, newTeam])}
                />
              )}
              type='primary'
            >
              + Adicionar Equipa
            </Button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <TeamsListComponent
              teams={teams}
            />
          </div>
        </div>
      </div>
  );
};

export default Equipas;
