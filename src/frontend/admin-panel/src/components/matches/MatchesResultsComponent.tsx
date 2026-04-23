import type { MatchDetail } from "../../api/matches";
import MatchPublishResultsModal from "./MatchPublishResultsModal";
import Button from "../utils/Button";
import { useModal } from "../../contexts/ModalContext";


const MatchResultsComponent = ( {
    matchState
} : {
    matchState: [MatchDetail, React.Dispatch<React.SetStateAction<MatchDetail | null>>];
} ) => {

    const [match, setMatch] = matchState;
    const { pushModal } = useModal();

    const renderPosition = (position: number | null) => {
        if (position === null) return '-';
        if (position === 1) return '1º Lugar';
        if (position === 2) return '2º Lugar';
        if (position === 3) return '3º Lugar';
        return `${position}º Lugar`;
    };

    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">
            Resultados do Jogo
          </h2>

          <Button
            onClick={() =>
              pushModal(
                <MatchPublishResultsModal
                  match={match}
                  onSave={(updatedMatch) => setMatch(updatedMatch)}
                />,
              )
            }
            type="primary"
          >
            Publicar Resultados
          </Button>
        </div>

        <div className="space-y-4">
          {match.participants.map((participant, index) => (
            <div
              key={index}
              className="flex items-center gap-4 p-4 bg-gray-50 rounded-md"
            >
              <div>
                {participant.score !== null && (
                  <p className="text-lg font-bold text-gray-800">
                    {participant.score}
                  </p>
                )}
                {participant.position !== null && (
                  <p className="text-lg font-bold text-gray-800">
                    {renderPosition(participant.position!)}
                  </p>
                )}
              </div>
              <p className="text-lg font-medium text-gray-700">
                {participant.name || `Participante ${index + 1}`}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
}

export default MatchResultsComponent;
