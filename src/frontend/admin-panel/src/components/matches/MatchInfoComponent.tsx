import { useState } from "react";
import { matchesApi, type MatchDetail } from "../../api/matches";
import HelpTooltip from "../HelpTooltip";
import { btn } from "../../styles/buttonStyles";
import { useNotification } from "../../contexts/NotificationProvider";

const MatchInfoComponent = ( {
    match,
    onMatchUpdated
} : {
    match: MatchDetail;
    onMatchUpdated?: (updatedMatch: MatchDetail) => void;
} ) => {
    const { notify } = useNotification();

    const [isEditingInfo, setIsEditingInfo] = useState(false);
    const [editedLocation, setEditedLocation] = useState<string>(match.location);
    const [editedStartTime, setEditedStartTime] = useState<string>(match.start_time);
    const [editedStatus, setEditedStatus] = useState<string>(match.status);
    const [saving, setSaving] = useState(false);

    const formatDateTime = (dateString: string) => {
      try {
        return new Date(dateString).toLocaleString("pt-PT", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      } catch (error) {
        console.error("Error formatting date:", error);
        return dateString;
      }
    };

    const renderNotEditingView = () => {
        return (
            <div className="space-y-4">
                <div className="border-b pb-3">
                    <label className="block text-sm font-medium text-gray-500 mb-1">Local</label>
                    <p className="text-lg text-gray-800">{match.location}</p>
                </div>

                <div className="border-b pb-3">
                    <label className="block text-sm font-medium text-gray-500 mb-1">Data e Hora</label>
                    <p className="text-lg text-gray-800">{formatDateTime(match.start_time)}</p>
                </div>
            </div>
        );
    };

    const onCancel = () => {
        setEditedLocation(match.location);
        setEditedStartTime(match.start_time);
        setEditedStatus(match.status);
        setIsEditingInfo(false);
    }

    const onSave = async () => {
        if (!match) return;

        if (!editedLocation.trim()) {
            notify('O local é obrigatório', 'error');
            return;
        }

        if (!editedStartTime.trim()) {
            notify('A data e hora são obrigatórias', 'error');
            return;
        }

        setSaving(true);
        try {
            const updatedMatch = await matchesApi.update(match.id, {
                location: editedLocation,
                start_time: editedStartTime,
                status: editedStatus,
            });
            // Update local state with new match details
            setIsEditingInfo(false);
            if (onMatchUpdated) onMatchUpdated(updatedMatch);
        } catch (error) {
            console.error("Failed to update match:", error);
        } finally {
            setSaving(false);
        }
    }

    const renderEditingView = () => {
      return (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado{" "}
              <HelpTooltip
                text="Agendado: jogo ainda não começou. Em Curso: jogo a decorrer. Terminado: jogo concluído com resultados registados. Cancelado: jogo cancelado sem resultados."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <select
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              value={editedStatus}
              onChange={() => setEditedStatus((prev) => {
                if (prev === "scheduled") return "in_progress";
                if (prev === "in_progress") return "finished";
                if (prev === "finished") return "cancelled";
                return "scheduled";
              }
            )}
            >
              <option value="scheduled">Agendado</option>
              <option value="in_progress">Em Curso</option>
              <option value="finished">Terminado</option>
              <option value="cancelled">Cancelado</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Local{" "}
              <HelpTooltip
                text="Local físico onde o jogo vai decorrer/decorreu, ex: Campo Municipal, Pav. Principal. Visível aos participantes."
                className="ml-1"
              />{" "}
              <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              value={editedLocation}
              onChange={() => setEditedLocation((prev) => prev === null ? "" : prev)}
              placeholder="Ex: Campo Municipal"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data e Hora <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              value={editedStartTime}
              onChange={() => setEditedStartTime((prev) => prev === null ? "" : prev)}
              required
            />
          </div>

          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onCancel}
              disabled={saving}
              className={`flex-1 px-4 py-2 ${btn.secondaryAlt} rounded-md font-medium transition-colors disabled:opacity-50`}
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={onSave}
              disabled={saving}
              className={`flex-1 px-4 py-2 ${btn.primary} rounded-md font-medium transition-colors disabled:opacity-50 flex items-center justify-center`}
            >
              {saving ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  A Guardar...
                </>
              ) : (
                "Guardar"
              )}
            </button>
          </div>
        </div>
      );
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-800">Informações</h3>
                {!isEditingInfo && (
                    <button
                    onClick={() => setIsEditingInfo(true)}
                    className="text-teal-600 hover:text-teal-700 p-1"
                    title="Editar"
                    >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    </button>
                )}
            </div>

            {isEditingInfo ? renderEditingView() : renderNotEditingView()}
        </div>
    );

}

export default MatchInfoComponent;
