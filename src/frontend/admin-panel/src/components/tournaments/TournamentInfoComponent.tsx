import { tournamentsApi, type TournamentDetail } from "../../api/tournaments";
import TournamentEditModal from "./TournamentEditModal";
import TournamentFinishModal from "./TournamentFinishModal";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";
import { useAuth } from "../../hooks/useAuth";

// Helper functions to get status text and badge color
const getStatusBadgeColor = (status: string) => {
  switch (status) {
    case 'active': return 'bg-green-100 text-green-800';
    case 'draft': return 'bg-yellow-100 text-yellow-800';
    case 'finished': return 'bg-gray-100 text-gray-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return 'Ativo';
    case 'draft': return 'Rascunho';
    case 'finished': return 'Finalizado';
    default: return status;
  }
};


const TournamentInfoComponent = ({
  tournamentState,
  onDelete,
}: {
  tournamentState: [TournamentDetail, React.Dispatch<React.SetStateAction<TournamentDetail | null>>]
  onDelete?: () => void;
}) => {

  const [tournament, setTournament] = tournamentState;
  const { pushModal } = useModal();
  const { isAdminGeneral } = useAuth();

  const handleActivate = async () => {
    if (!tournament) return;
    try {
      let result = await tournamentsApi.update(tournament.id, { status: 'active' });
      setTournament(result);
    } catch (error) {
      console.error("Failed to activate tournament:", error);
    }
  };

  const handleDelete = async () => {
    if (!tournament) return;
    try {
      await tournamentsApi.delete(tournament.id);
      if (onDelete) onDelete();
    } catch (error) {
      console.error("Failed to delete tournament:", error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">

      <div>
        <label className="block text-teal-500 font-medium mb-2">
          Modalidade
        </label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
          {tournament.modality.name}
        </div>
      </div>

      <div>
        <label className="block text-teal-500 font-medium mb-2">
          Temporada
        </label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
          {tournament.season.name}
        </div>
      </div>

      <div>
        <label className="block text-teal-500 font-medium mb-2">Estado</label>
        <div className="w-full px-4 py-3 bg-gray-100 rounded-md">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeColor(tournament.status)}`}
          >
            {getStatusText(tournament.status)}
          </span>
        </div>
      </div>

      {tournament.start_date && (
        <div>
          <label className="block text-teal-500 font-medium mb-2">
            Data de Início
          </label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800">
            {new Date(tournament.start_date).toLocaleDateString("pt-PT")}
          </div>
        </div>
      )}

      {tournament.scoring_format && (
        <div>
          <label className="block text-teal-500 font-medium mb-2">
            Formato de Pontuação
          </label>
          {/* circle with rank */}
          <div className="w-full px-4 py-3 bg-gray-100 rounded-md text-gray-800 flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-teal-500 text-white flex items-center justify-center text-xs font-medium">
              {tournament.scoring_format.rank}
            </span>
            {tournament.scoring_format.name}
          </div>
        </div>
      )}

      <div className="flex gap-4 pt-4">
        <Button
          onClick={() => pushModal(
            <TournamentEditModal
              tournamentState={[tournament, setTournament]}
            />
          )}
          type="primary"
          flexible={true}
          active={isAdminGeneral}
        >
          Editar
        </Button>
        <Button
          onClick={handleDelete}
          type="danger"
          confirmation={{
            title: "Eliminar torneio",
            message: tournament ? `Tem certeza que deseja eliminar "${tournament.name}"?` : '',
            confirmLabel: "Eliminar",
          }}
          flexible={true}
          active={isAdminGeneral}
        >
          Eliminar
        </Button>
      </div>

      {isAdminGeneral && (
        <div className="flex gap-4 pt-4 border-t mt-4">

          {tournament.status === "draft" && (
            <Button
              onClick={handleActivate}
              type="success"
              confirmation={{
                title: "Ativar torneio",
                message: tournament ? `Tem certeza que deseja ativar "${tournament.name}"?` : '',
                confirmLabel: "Ativar",
              }}
              flexible={true}
            >
              Ativar Torneio
            </Button>
          )}

          {tournament.status === "active" && (
            <Button
              onClick={() => pushModal(
                <TournamentFinishModal
                  tournamentState={[tournament, setTournament]}
                />
              )}
              type="info"
              flexible={true}
            >
              Finalizar Torneio
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default TournamentInfoComponent;
