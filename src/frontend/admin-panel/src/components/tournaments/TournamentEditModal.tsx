import React, { useState } from "react";
import { tournamentsApi, type TournamentDetail } from "../../api/tournaments";
import HelpTooltip from "../HelpTooltip";
import Button from "../utils/Button";

const TournamentEditModal = ({
  controller,
  tournament,
  onSave,
}: {
  controller: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
  tournament: TournamentDetail;
  onSave: (updatedTournament: TournamentDetail) => void;
}) => {
  const [isOpen, setIsOpen] = controller;

  const [name, setName] = useState(tournament.name);
  const [startDate, setStartDate] = useState(tournament.start_date || "");
  const [isPlayoff, setIsPlayoff] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    setSaving(true);
    try {
      const updated = await tournamentsApi.update(tournament.id, {
        name: name.trim(),
        start_date: startDate || undefined,
        is_playoff: isPlayoff,
      });
      onSave(updated);
      setIsOpen(false);
    } catch (error) {
      console.error("Erro ao atualizar torneio:", error);
      alert("Ocorreu um erro ao atualizar o torneio. Tente novamente.");
    } finally {
      setSaving(false);
    }
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

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_playoff_edit"
              checked={isPlayoff}
              onChange={(e) => setIsPlayoff(e.target.checked)}
              className="w-4 h-4 accent-teal-500"
            />
            <label
              htmlFor="is_playoff_edit"
              className="text-gray-700 font-medium cursor-pointer"
            >
              Torneio de Playoff
            </label>
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
