import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import TournamentList from '../../components/tournaments/TournamentList';
import TournamentCreateModal from '../../components/tournaments/TournamentCreateModal';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import { useAuth } from '../../hooks/useAuth';
import TeamsListComponent from '../../components/teams/TeamsListComponent';
import TabSystem from '../../components/TabSystem';
import ModalityInfoComponent from '../../components/modalities/ModalityInfoComponent';
import { useNotification } from '../../contexts/NotificationProvider';
import { type TeamListItem } from '../../api/teams';
import { useSeason } from '../../contexts/SeasonContext';
import SeasonSelector from '../../components/seasons/SeasonSelector';
import MatchesCalendarComponent from '../../components/matches/MatchesCalendarComponent';


const TournamentsTab = ({
  modality,
  tournamentsState
}: {
  modality: ModalityDetail;
  tournamentsState?: [TournamentListItem[] | null, React.Dispatch<React.SetStateAction<TournamentListItem[] | null>>]
}) => {
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();
  const { notify } = useNotification();
  const { loadedSeason } = useSeason();

  const [tournaments, setTournaments] = tournamentsState || useState<TournamentListItem[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateTournament = (newTournament: TournamentListItem) => {
    setTournaments([...(tournaments || []), newTournament]);
  };

  useEffect(() => {
    if (!modality.belongs_to_season) return;
    setIsLoading(true);
    tournamentsApi.getAll({ modality_id: modality.id, season_id: loadedSeason?.id })
      .then((data) => setTournaments(data))
      .catch((error) => {
        console.error('Erro ao carregar torneios:', error);
        setTournaments(null);
        notify('Falha ao carregar torneios para esta modalidade.', 'error');
      })
      .finally(() => setIsLoading(false));
  }, [modality.id, modality.belongs_to_season, loadedSeason?.id]);

  const renderTournamentList = () => {
    if (isLoading) {
      return <div className="text-gray-500">Carregando torneios...</div>;
    }

    if (!tournaments) {
      return <div className="text-red-500">Erro ao carregar torneios.</div>;
    }

    return <TournamentList
      tournaments={tournaments}
      displayModality={false}
      showModalityFilter={false}
    />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        {/* <h2 className="text-xl font-semibold text-gray-800">{tournaments.length} Torneios</h2> */}
        <Button
          onClick={() => pushModal(
            <TournamentCreateModal
              onCreate={handleCreateTournament}
              modalityId={modality.id}
              starterName={`Torneio ${modality.name}`}  // Pre-fill with a default name
            />
          )}
          type='primary'
          active={isAdminGeneral}
          flexible={true}
        >
          + Criar Torneio
        </Button>
      </div>

      { renderTournamentList() }
    </div>
  );
};

function ModalidadeDetail() {
  const modalityId = useParams<{ id: string }>().id;
  if (!modalityId) {
    return <div className="text-red-500">ID de modalidade não fornecido.</div>;
  }

  const { notify } = useNotification();
  const navigate = useNavigate();
  const { loadedSeason } = useSeason();

  const [modality, setModality] = useState<ModalityDetail | null>(null);

  const [tournaments, setTournaments] = useState<TournamentListItem[] | null>(null); // Estado para armazenar os torneios, passado para o TabSystem
  const [teams, setTeams] = useState<TeamListItem[] | null>(null); // Estado para armazenar as equipas, passado para o TabSystem

  useEffect(() => {
    modalitiesApi.getById(modalityId, loadedSeason?.id)
      .then((data) => setModality(data))
      .catch((error) => {
        console.error('Erro ao carregar modalidade:', error);
        setModality(null);
        notify('Falha ao carregar detalhes da modalidade.', 'error');
      });
  }, [modalityId, loadedSeason?.id]);

  if (!modality) {
    return <div className="text-red-500">Modalidade não encontrada.</div>;
  }

  return (
    <>
      <SeasonSelector relevantSeasonIds={modality.relevant_seasons_ids} />
      <div className="flex-1 p-8 max-w-5xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes da Modalidade</h1>
          <Button
            onClick={() => navigate('/modalidades')}
            type='secondary'
            padding='px-6 py-3'
          >
            Voltar
          </Button>
        </div>

        {/* Modality Information - Always visible at top */}
        <ModalityInfoComponent modalityState={[modality, setModality]} />
      </div>
      { modality.belongs_to_season && (
        <div className="flex-1 max-w-7xl mx-auto">
          <TabSystem
            elements={[
              { id: 'tournaments', label: 'Torneios', content: <TournamentsTab modality={modality} tournamentsState={[tournaments, setTournaments]} /> },
              { id: 'teams', label: 'Equipas', content: <TeamsListComponent modalityId={modality.id} teamsState={[teams, setTeams]} /> },
              { id: 'matches', label: 'Jogos', content: <MatchesCalendarComponent modalityId={modality.id} /> },
            ]}
          />
        </div>
      )}
    </>
  );
}

export default ModalidadeDetail;
