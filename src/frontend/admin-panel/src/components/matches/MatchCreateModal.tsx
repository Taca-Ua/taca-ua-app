import { useState } from "react";
import { matchesApi, type MatchListItem } from "../../api/matches"
import { type TournamentDetail } from "../../api/tournaments";
import HelpTooltip from "../HelpTooltip";
import ChooseMultipleModal from "../utils/costum_menus/ChoseMultipleModal";
import { useNotification } from "../../contexts/NotificationProvider";
import Button from "../utils/Button";

const MatchCreateModal = ( {
  controller,
  tournament,
  onCreated,
} : {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>],
  tournament: TournamentDetail,
  onCreated?: (match: MatchListItem) => void
} ) => {
  const { notify } = useNotification();

  const [isOpen, setIsOpen] = controller;

  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  const [location, setLocation] = useState<string>("");
  const [startTime, setStartTime] = useState<string>("");
  const [loading, setLoading] = useState<boolean>( false );

  const choseParticipantsController = useState<boolean>( false );

  const handleCreateMatch = async () => {
    if (selectedParticipants.length < 2 || selectedParticipants.includes("")) {
      notify("Por favor, selecione pelo menos 2 participantes para o jogo.", "error");
      return;
    }
    if (!location.trim()) {
      notify("Por favor, insira o local do jogo.", "error");
      return;
    }
    if (!startTime) {
      notify("Por favor, selecione a data e hora do jogo.", "error");
      return;
    }

    setLoading( true );
    try {
      let newMatch = await matchesApi.create( {
        tournament_id: tournament.id,
        participants: selectedParticipants,
        location,
        start_time: startTime
      } );
      notify("Jogo criado com sucesso!", "success");
      // Aqui você pode adicionar lógica para fechar o modal ou atualizar a lista de jogos
      if (onCreated) onCreated(newMatch);
      setIsOpen(false);
    } catch ( error ) {
      console.error( "Error creating match:", error );
      notify("Ocorreu um erro ao criar o jogo. Por favor, tente novamente.", "error");
    } finally {
      setLoading( false );
    }
  };

  if ( !isOpen ) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Criar Jogo</h2>

        <div className="space-y-4">
          {/* Participantes */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-gray-700 font-medium">
                Participantes{" "}
                <HelpTooltip
                  text="Selecione os competidores que vão disputar este jogo. São necessários no mínimo 2 participantes. Só podem ser selecionados competidores já inscritos no torneio."
                  className="ml-1"
                />{" "}
                <span className="text-red-500">*</span>
              </label>
              <div>
                <Button
                  onClick={() => choseParticipantsController[1]( true )}
                  type="info"
                  flexible={true}
                  padding="px-4 py-2"
                >
                  +/- Editar Participantes
                </Button>
              </div>
            </div>
            <ChooseMultipleModal
              controller={choseParticipantsController}
              allElementsLoader={async () => tournament.competitors.map(competitor => ({
                id: competitor.id,
                title: competitor.name,
                subTitle: competitor.course_name
              }))}
              initialChosenElementsIds={selectedParticipants}
              onSave={(chosenIds) => setSelectedParticipants(chosenIds.map(ele => ele.id))}
              showSummary={true}
              title="Selecionar Participantes do Jogo"
            />

            <div className="space-y-2">
              {selectedParticipants.map((participantId, index) => (
                <div key={index} className="flex gap-2">
                  <div className="flex-1 px-4 py-2 border border-gray-300 rounded-md bg-gray-100 text-gray-700">
                    {participantId
                      ? tournament.competitors.find(c => c.id === participantId)?.name || "Participante não encontrado"
                      : "Nenhum participante selecionado"}
                  </div>
                </div>
              ))}
            </div>
            {selectedParticipants.length < 2 && (
              <p className="text-sm text-gray-500 mt-1">
                Mínimo de 2 participantes necessários
              </p>
            )}
          </div>

          {/* Local */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Local{" "}
              <HelpTooltip
                text="Local onde o jogo vai decorrer, ex: Campo Municipal, Pavilhão Principal. Esta informação é visível aos participantes."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Ex: Campo Municipal"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 text-gray-700"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Data e Hora <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 text-gray-700"
            />
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <Button
            onClick={() => setIsOpen(false)}
            type="secondary"
            flexible={true}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleCreateMatch}
            type="primary"
            flexible={true}
          >
            {loading ? "A criar..." : "Criar"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default MatchCreateModal
