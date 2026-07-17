import { useEffect, useState } from "react";
import { rankingApi, type RankingAmmendment } from "../../api/ranking";
import { useSeason } from "../../contexts/SeasonContext";
import { useNotification } from "../../contexts/NotificationProvider";
import LazyImage from "../utils/LazyImage";


const AmmedmentItem = ({ ammendment }: { ammendment: RankingAmmendment }) => {

    const renderPoints = (points: number) => {
        if (points > 0) {
            return <span className="text-green-600">+{points}</span>;
        } else if (points < 0) {
            return <span className="text-red-600">{points}</span>;
        }
        return <span className="text-gray-600">0</span>;
    }

        return (
        <div className="flex gap-1 p-2 border rounded justify-between items-center px-10">
            <div className="flex items-center gap-2">
                {ammendment.course.logo_url ? (
                    <LazyImage src={ammendment.course.logo_url} alt={ammendment.course.name} className="w-24 h-24 object-contain" />
                ) :
                    <div className="w-12 h-12 bg-gray-200 flex items-center justify-center rounded">
                        <span className="text-gray-500 text-sm">{ammendment.course.name[0]}</span>
                    </div>
                }
                <span className="font-semibold">{ammendment.course.name}</span>
            </div>

            <div className={"text-sm text-gray-600 border border-gray-300 p-1 rounded block w-1/4 h-full text-center" + (ammendment.reason ? "" : " italic")}>
                {ammendment.reason ?
                    <span className="text-black font-semibold">{ammendment.reason}</span>
                : "Sem motivo"}
            </div>
            <div className={"text-sm text-gray-600 border border-gray-300 p-1 rounded block w-1/4 h-full text-center" + (ammendment.modality ? "" : " italic")}>
                {ammendment.modality ?
                    <span className="text-black font-semibold">{ammendment.modality.name}</span>
                : "Sem modalidade"}
            </div>

            <div className="font-bold">{renderPoints(ammendment.points)}</div>
        </div>
    );
}


const AmmedmentListComponent = ({
    ammendmentsState,
} : {
    ammendmentsState?: [RankingAmmendment[], React.Dispatch<React.SetStateAction<RankingAmmendment[]>>];
}) => {
    const { loadedSeason } = useSeason();
    const { notify } = useNotification();

    const [ammendments, setAmmendments] = ammendmentsState || useState<RankingAmmendment[]>([]);

    useEffect(() => {
        if (!loadedSeason) return;

        rankingApi.getRankingAmmendments(loadedSeason.id).then((response) => {
            setAmmendments(response);
        }).catch((error) => {
            console.error("Failed to fetch ranking amendments:", error);
            notify("Falha ao carregar as alterações do ranking.", "error");
        })
    }, [loadedSeason]);

    return (
        <div className="flex flex-col gap-2">
            {ammendments.map((ammendment, index) => (
                <AmmedmentItem key={index} ammendment={ammendment} />
            ))}
        </div>
    );
};

export default AmmedmentListComponent;
