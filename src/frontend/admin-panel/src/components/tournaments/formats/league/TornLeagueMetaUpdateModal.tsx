import { useEffect, useState } from "react";
import { type TournamentDetail, tournamentsApi } from "../../../../api/tournaments"
import { useModal } from "../../../../contexts/ModalContext";
import { useNotification } from "../../../../contexts/NotificationProvider";
import Button from "../../../utils/Button";
import DefinedStatesMenuComponent from "../../../utils/costum_menus/DefinedStatesMenuComponent";

const TornLeagueMetaUpdateModal = ({
    tournamentState,
    onSave,
} : {
    tournamentState: [TournamentDetail, React.Dispatch<React.SetStateAction<TournamentDetail | null>>],
    onSave?: (updatedTournament: TournamentDetail) => void
}) => {
    const { popModal } = useModal();
    const { notify } = useNotification();

    const [tournament, setTournament] = tournamentState;
    const [loading, setLoading] = useState(false);

    const [pointsWin, setPointsWin] = useState(tournament.format_data?.points_win);
    const [pointsDraw, setPointsDraw] = useState(tournament.format_data?.points_draw);
    const [pointsLoss, setPointsLoss] = useState(tournament.format_data?.points_loss);
    const [tiebreaker, setTiebreaker] = useState(tournament.format_data?.points_diff_tiebreaker || "none");

    useEffect(() => {
        if (!tournament.format_data){
            notify("Dados de formato não encontrados para este torneio.", "error");
        }

        setPointsWin(tournament.format_data?.points_win);
        setPointsDraw(tournament.format_data?.points_draw);
        setPointsLoss(tournament.format_data?.points_loss);
        setTiebreaker(tournament.format_data?.points_diff_tiebreaker || "none");
    }, []);

    const onClose = () => {
        popModal();
    }

    const handleSave = () => {
        if (pointsWin === undefined || pointsDraw === undefined || pointsLoss === undefined) {
            notify("Por favor, preencha todos os campos de pontos.", "error");
            return;
        }

        setLoading(true);
        tournamentsApi.updateFormatMeta(tournament.id, {
            win_points: pointsWin,
            draw_points: pointsDraw,
            loss_points: pointsLoss,
            points_diff_tiebreaker: tiebreaker
        }).then((updatedTournament) => {
            setTournament(updatedTournament);
            if (onSave) {
                onSave(updatedTournament);
            }
            notify("Configurações de pontuação atualizadas com sucesso!", "success");
            popModal();
        }).catch(() => {
            notify("Erro ao atualizar as configurações de pontuação. Por favor, tente novamente.", "error");
        }).finally(() => {
            setLoading(false);
        });
    }

    return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[700px]">
        <h2 className="text-2xl font-bold mb-6">Editar Pontuação da Liga</h2>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Pontos por Vitória</label>
          <input
            type="number"
            value={pointsWin}
            onChange={(e) => setPointsWin(parseInt(e.target.value))}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Pontos por Empate</label>
          <input
            type="number"
            value={pointsDraw}
            onChange={(e) => setPointsDraw(parseInt(e.target.value))}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Pontos por Derrota</label>
          <input
            type="number"
            value={pointsLoss}
            onChange={(e) => setPointsLoss(parseInt(e.target.value))}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
        <div className="space-y-2 my-4">
          <label className="block text-sm font-medium text-gray-700">
            Critério de Desempate por Diferença de Pontos
          </label>
          <DefinedStatesMenuComponent
            states={[
              { value: "none", label: "Nenhum" },
              { value: "points_difference", label: "Diferença de Pontos" },
              { value: "scored_points", label: "Pontos Marcados" },
            ]}
            initialValue={tiebreaker}
            onSelect={(value) => setTiebreaker(value)}
          />
        </div>
        <div className="flex justify-end space-x-4 mt-6">
          <Button onClick={onClose} type="secondary" flexible={true} disabled={loading}>
            Cancelar
          </Button>
          <Button onClick={handleSave} type="primary" flexible={true} disabled={loading}>
            Salvar
          </Button>
        </div>
      </div>
    );
}

export default TornLeagueMetaUpdateModal;
