import { btn } from "../../styles/buttonStyles";
import HelpTooltip from "../HelpTooltip";
import { matchesApi } from "../../api/matches";
import { tournamentsApi } from "../../api/tournaments";
import { useEffect, useState } from "react";

const CreateMatchComponent = () => {

  const [showCreateModal, setShowCreateModal] = useState(true);

  const [selectedParticipants, setSelectedParticipants] = useState<string[]>(["", ""]);
  const [location, setLocation] = useState("");
  const [startTime, setStartTime] = useState("");
  const [loading, setLoading] = useState(false);

  const [tournamentCompetitors, setTournamentCompetitors] = useState<{ id: string; full_name: string }[]>([]);

  useEffect(() => {
    // get competitors for the tournament to populate the dropdown
    const fetchCompetitors = async () => {
      try {
        const tournamentId = "tournament-id-placeholder"; // Substitua pelo ID real do torneio
        const data = await tournamentsApi.getById(tournamentId);
        setTournamentCompetitors(data.competitors.map((comp) => ({ id: comp.id, full_name: comp.name })));
      } catch (error) {
        console.error("Erro ao buscar competidores do torneio:", error);
        alert("Ocorreu um erro ao buscar os competidores do torneio. Por favor, tente novamente.");
      }
    };
    fetchCompetitors();
  }, []);

  const addParticipantSlot = () => {
    setSelectedParticipants([...selectedParticipants, ""]);
  };

  const removeParticipantSlot = (index: number) => {
    const updatedParticipants = [...selectedParticipants];
    updatedParticipants.splice(index, 1);
    setSelectedParticipants(updatedParticipants);
  };

  const updateParticipant = (index: number, value: string) => {
    const updatedParticipants = [...selectedParticipants];
    updatedParticipants[index] = value;
    setSelectedParticipants(updatedParticipants);
  };

  const handleCreateMatch = async () => {
    if (selectedParticipants.length < 2) {
      alert("É necessário selecionar pelo menos 2 participantes.");
      return;
    }
    if (!location.trim()) {
      alert("O campo de local é obrigatório.");
      return;
    }
    if (!startTime) {
      alert("O campo de data e hora é obrigatório.");
      return;
    }
    setLoading(true);
    try {
      await matchesApi.create({
        tournament_id: "tournament-id-placeholder", // Substitua pelo ID real do torneio
        location,
        start_time: startTime,
        competitors: selectedParticipants,
      });
      alert("Jogo criado com sucesso!");
      setShowCreateModal(false);
    } catch (error) {
      console.error("Erro ao criar jogo:", error);
      alert("Ocorreu um erro ao criar o jogo. Por favor, tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Criar Jogo</h2>

        <div className="space-y-4">
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
              <button
                type="button"
                onClick={addParticipantSlot}
                className={`text-sm px-3 py-1 ${btn.info} rounded-md transition-colors`}
              >
                + Adicionar Participante
              </button>
            </div>
            <div className="space-y-2">
              {selectedParticipants.map((participantId, index) => (
                <div key={index} className="flex gap-2">
                  <select
                    value={participantId}
                    onChange={(e) => updateParticipant(index, e.target.value)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Selecione um participante</option>
                    {tournamentCompetitors.map((competitor) => {
                      const label = competitor.full_name; // Exibir o nome completo do competidor (equipe ou atleta)

                      return (
                        <option
                          key={`${competitor.id}`}
                          value={competitor.id}
                        >
                          {label}
                        </option>
                      );
                    })}
                  </select>
                  {selectedParticipants.length > 2 && (
                    <button
                      type="button"
                      onClick={() => removeParticipantSlot(index)}
                      className={`px-3 py-2 ${btn.dangerLight} rounded-md transition-colors`}
                      title="Remover participante"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Mínimo de 2 participantes necessários
            </p>
          </div>

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
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
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
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>
        </div>

        <div className="flex gap-4 mt-6">
          <button
            onClick={() => setShowCreateModal(false)}
            disabled={loading}
            className={`flex-1 px-4 py-2 ${btn.secondary} rounded-md disabled:opacity-50`}
          >
            Cancelar
          </button>
          <button
            onClick={handleCreateMatch}
            disabled={loading}
            className={`flex-1 px-4 py-2 ${btn.primary} rounded-md disabled:opacity-50`}
          >
            {loading ? "A criar..." : "Criar"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateMatchComponent;
