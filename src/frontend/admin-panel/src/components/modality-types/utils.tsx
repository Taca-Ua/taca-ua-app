import type { ModalityTypeListItem } from "../../api/modality-types";

export const ModalityTypeBadge: React.FC<{ format: ModalityTypeListItem }> = ({ format }) => {
    return (
        <div className="flex items-center space-x-2">
        {(format.mode === "points") && (
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold border bg-amber-100 text-amber-700 border-amber-300">
                Pontuação
            </span>
        )}
        {(format.tournament_competitor_type === 'individual') && (
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border bg-blue-100 text-blue-700 border-blue-300`}>
                Individual
            </span>
        )}
        {(format.tournament_competitor_type === 'team') && (
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border bg-green-100 text-green-700 border-green-300`}>
                Equipa
            </span>
        )}
        </div>
    );
};
