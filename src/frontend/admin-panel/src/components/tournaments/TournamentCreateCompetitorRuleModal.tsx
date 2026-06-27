import { useState } from "react";
import { useModal } from "../../contexts/ModalContext";
import ChoseOneInput from "../utils/inputs/ChoseOneInput";
import { tournamentsApi, type TournamentListItem } from '../../api/tournaments';
import Button from "../utils/Button";
import HelpTooltip from "../HelpTooltip";
import { useNotification } from "../../contexts/NotificationProvider";

export interface CompetitorRule {
    targetTournament: TournamentListItem;
    startingPosition: number;
    endingPosition: number;
}

const TournamentCreateCompetitorRuleModal = ({
    modalityId,
    onSave,
} : {
    modalityId: string;
    onSave?: (rule: CompetitorRule) => void;
}) => {
    const { popModal } = useModal();
    const { notify } = useNotification();

    const [targetTournament, setTargetTournament] = useState<TournamentListItem | null>(null);
    const [startingPosition, setStartingPosition] = useState<number | null>(null);
    const [endingPosition, setEndingPosition] = useState<number | null>(null);

    const handleClose = () => {
        popModal();
    }

    const handleSave = () => {
        if (!targetTournament) {
            notify('Por favor, selecione um torneio de origem.', 'error');
            return;
        }

        if (startingPosition === null || endingPosition === null) {
            notify('Por favor, defina a faixa de classificação do torneio de origem.', 'error');
            return;
        }

        if (startingPosition < 1 || endingPosition < 1 || startingPosition > endingPosition) {
            notify('Por favor, defina uma faixa de classificação válida. A posição inicial deve ser menor ou igual à posição final e ambas devem ser maiores que zero.', 'error');
            return;
        }

        // Here you would gather the data for the rule and call onSave
        const ruleData = {
            targetTournament: targetTournament,
            startingPosition,
            endingPosition,
        };

        if (onSave) onSave(ruleData);
        handleClose();
    }

    return (
      <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[700px]">
        <h2 className="text-xl font-semibold mb-4">Adicionar Regra de Qualificação</h2>
        <div className="space-y-4">
            <label className="font-medium">
                Torneio de Origem{' '}
                <span className="text-red-500">*</span>
                <HelpTooltip
                    text="Selecione o torneio do qual os competidores serão qualificados para este torneio. Apenas torneios da mesma modalidade estão disponíveis."
                    className="ml-1"
                />
            </label>
            <ChoseOneInput
                allElementsLoader={() => tournamentsApi.getAll({modality_id: modalityId}).then(res => res.map(t => ({ id: t.id, title: t.name, object: t })))}
                onSelect={(ele) => {
                    if (!ele) return;
                    setTargetTournament(ele.object);
                }}
            />
        </div>

        {/* Target Tournament Standings Range */}
        {targetTournament && (
            <div className="space-y-4 mt-4">
                <label className="font-medium">
                    Faixa de Classificação do Torneio de Origem{' '}
                    <span className="text-red-500">*</span>
                    <HelpTooltip
                        text="Defina a faixa de classificação do torneio de origem que será qualificada para este torneio. Por exemplo, se você definir '1-3', os três primeiros classificados do torneio de origem serão qualificados."
                        className="ml-1"
                    />
                </label>
                <div className="flex space-x-2">
                    <input
                        type="number"
                        placeholder="Posição Inicial"
                        className="w-full border border-gray-300 rounded-md p-2"
                        onChange={(e) => setStartingPosition(Number(e.target.value))}
                    />
                    <input
                        type="number"
                        placeholder="Posição Final"
                        className="w-full border border-gray-300 rounded-md p-2"
                        onChange={(e) => setEndingPosition(Number(e.target.value))}
                    />
                </div>
            </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-2 mt-4">
        <Button
            onClick={handleClose}
            type="secondary"
            flexible={true}
        >
            Cancelar
        </Button>
        <Button
            onClick={handleSave}
            type="primary"
            flexible={true}
        >
            Salvar
        </Button>
        </div>
      </div>
    );
}

export default TournamentCreateCompetitorRuleModal;
