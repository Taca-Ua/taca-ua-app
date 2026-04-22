import React, { useEffect, useState } from "react";
import { tournamentsApi, type TournamentDetail } from "../../api/tournaments";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";
import { useNotification } from "../../contexts/NotificationProvider";

const TournamentEditModal = ({
  controller,
  tournamentState,
  onSave,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  tournamentState: [TournamentDetail, React.Dispatch<React.SetStateAction<TournamentDetail | null>>];
  onSave?: (updatedTournament: TournamentDetail) => void;
}) => {
  const [isOpen, setIsOpen] = controller;
  const [tournament, setTournament] = tournamentState;
  const { notify } = useNotification();

  const [name, setName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    setName(tournament.name);
    setStartDate(tournament.start_date ? tournament.start_date.split('T')[0] : "");
  }, [isOpen, tournament]);

  const handleSubmit = () => {

    if (!name.trim()) {
      notify("Por favor, preencha o nome do torneio.", 'error');
      return;
    }

    setSaving(true);
    tournamentsApi.update(tournament.id, {
      name: name.trim(),
      start_date: startDate || undefined,
    }).then((updated) => {
      setTournament(updated);
      if(onSave) onSave(updated);
      setIsOpen(false);
      notify("Torneio atualizado com sucesso!", 'success');
    }).catch((error) => {
      console.error("Erro ao atualizar torneio:", error);
      notify("Ocorreu um erro ao atualizar o torneio. Tente novamente.", 'error');
    }).finally(() => {
      setSaving(false);
    });
  };

  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          Editar Torneio
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Nome <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Data de Início{" "}
              <HelpTooltip
                text="Data em que o torneio começa oficialmente. Após esta data o torneio pode ser ativado e os jogos calendarizados."
                className="ml-1"
              />
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500"
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
            onClick={handleSubmit}
            type="primary"
            flexible={true}
          >
            {saving ? "A guardar..." : "Guardar"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TournamentEditModal;
