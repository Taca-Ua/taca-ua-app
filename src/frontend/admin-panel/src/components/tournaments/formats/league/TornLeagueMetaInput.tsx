import { useEffect, useState } from "react";
import DefinedStatesMenuComponent from "../../../utils/costum_menus/DefinedStatesMenuComponent";

const TornLeagueMetaInput = ({ data } : { data: Record<string, unknown> }) => {
    const [winPoints, setWinPoints] = useState(3);
    const [drawPoints, setDrawPoints] = useState(1);
    const [lossPoints, setLossPoints] = useState(0);
    const [tiebreaker, setTiebreaker] = useState("none");

    const handleDataChange = () => {
        // clear all data related to other formats to avoid confusion
        for (const key in data) {
            delete data[key];
        }

        data['win_points'] = winPoints;
        data['draw_points'] = drawPoints;
        data['loss_points'] = lossPoints;
        data['points_diff_tiebreaker'] = tiebreaker;
        console.log('Updated format data:', data);
    }

    useEffect(() => {
        handleDataChange();
    }, []);

    useEffect(() => {
        handleDataChange();
    }, [winPoints, drawPoints, lossPoints, tiebreaker]);

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700">Pontos por Vitória</label>
                <input
                    type="number"
                    value={winPoints}
                    onChange={(e) => setWinPoints(parseInt(e.target.value))}
                    className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700">Pontos por Empate</label>
                <input
                    type="number"
                    value={drawPoints}
                    onChange={(e) => setDrawPoints(parseInt(e.target.value))}
                    className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700">Pontos por Derrota</label>
                <input
                    type="number"
                    value={lossPoints}
                    onChange={(e) => setLossPoints(parseInt(e.target.value))}
                    className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
            </div>
            <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Critério de Desempate por Diferença de Pontos</label>
                <DefinedStatesMenuComponent
                    states={[
                        { value: "none", label: "Nenhum" },
                        { value: "points_difference", label: "Diferença de Pontos" },
                        { value: "points_scored", label: "Pontos Marcados" },
                    ]}
                    initialValue={tiebreaker}
                    onSelect={(value) => setTiebreaker(value)}
                />
            </div>
        </div>
    );
}

export default TornLeagueMetaInput;
