import { useModal } from "../../contexts/ModalContext";
import { type MatchDetail } from "../../api/matches";
import Button from "../utils/Button";
import MatchTeamLineupModal from "./MatchTeamLineupModal";

const LineupsSection = ({ match }: { match: MatchDetail }) => {
  const { pushModal } = useModal();

  const participants = match.participants;

  if (participants === null || participants === undefined) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>
        <p className="text-gray-600">Dados de convocatória não disponíveis.</p>
      </div>
    );
  }

  if (participants.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>
        <p className="text-gray-600">Nenhuma convocatória definida.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Convocatórias</h3>

      <div className="space-y-6">
          {participants?.map((participant) => {

            return (
              <div key={participant.id} className="border-l-4 border-teal-500 pl-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-lg text-gray-800">
                    {participant.name}
                  </h4>
                  <Button
                    onClick={() => {pushModal(
                      <MatchTeamLineupModal matchId={match.id} participantId={participant.id} />
                    )}}
                    type='info'
                    padding='px-10 py-2'
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
    </div>
  );
};

export default LineupsSection;
