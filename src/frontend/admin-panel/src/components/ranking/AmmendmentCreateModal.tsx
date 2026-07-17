import { useState } from "react";
import { rankingApi, type RankingAmmendment } from "../../api/ranking";
import { coursesApi } from "../../api/courses";
import { modalitiesApi } from "../../api/modalities";
import { useModal } from "../../contexts/ModalContext";
import { useNotification } from "../../contexts/NotificationProvider";
import { useSeason } from "../../contexts/SeasonContext";
import Button from "../utils/Button";
import ChoseOneInput from "../utils/inputs/ChoseOneInput";

const AmmendmentCreateModal = ({
    onCreate
} : {
    onCreate?: (amendment: RankingAmmendment) => void
}) => {
    const { popModal } = useModal();
    const { notify } = useNotification();
    const { loadedSeason } = useSeason();

    const [course, setCourse] = useState<any>(null);
    const [modality, setModality] = useState<any>(null);
    const [points, setPoints] = useState<number>(0);
    const [reason, setReason] = useState<string>("");

    const handleClose = () => {
        popModal();
    }

    const handleCreate = () => {
        if (!loadedSeason) return;

        if (!course) {
            notify("Por favor, selecione um curso.", "error");
            return;
        }

        rankingApi.createRankingAmmendment(loadedSeason.id, {
            course_id: course.id,
            points: points,
            reason: reason || undefined,
            modality_id: modality?.id || undefined
        }).then((response) => {
            if (onCreate) onCreate(response);
            notify("Alteração de rank criada com sucesso!", "success");
            handleClose();
        }).catch((error) => {
            console.error("Failed to create ranking amendment:", error);
            notify("Falha ao criar alteração de rank!", "error");
        });
    };

    const loadCourses = async () => {
        return coursesApi.getAll(loadedSeason?.id).then((response) => {
            return response.map(course => ({
                id: course.id,
                title: course.name,
                subTitle: course.abbreviation
            }));
        }).catch((error) => {
            console.error("Failed to load courses:", error);
            notify("Falha ao carregar cursos.", "error");
            return [] as {id: string, title: string, subTitle?: string}[];
        });
    }

    const loadModalities = async () => {
        if (!loadedSeason) return [] as {id: string, title: string, subTitle?: string}[];

        return modalitiesApi.getAll({season_id: loadedSeason.id}).then((response) => {
            return response.filter((modality) => modality.belongs_to_season).map(modality => ({
                id: modality.id,
                title: modality.name
            }));
        }).catch((error) => {
            console.error("Failed to load modalities:", error);
            notify("Falha ao carregar modalidades.", "error");
            return [] as {id: string, title: string, subTitle?: string}[];
        });
    }

    return (
        <div className="bg-white rounded-lg p-8 w-full max-w-md md:min-w-[500px]">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">
                Adicionar Alteração de Ranking
            </h2>

            <div className="space-y-4">
                <div>
                    <label className="block text-gray-700 font-medium mb-2">
                        Pontos <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="number"
                        value={points}
                        onChange={(e) => setPoints(Number(e.target.value))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                        placeholder="Digite os pontos"
                    />
                </div>

                <div>
                    <label className="block text-gray-700 font-medium mb-2">
                        Motivo
                    </label>
                    <textarea
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                        placeholder="Digite o motivo"
                    />
                </div>

                <div>
                    <label className="block text-gray-700 font-medium mb-2">
                        Curso <span className="text-red-500">*</span>
                    </label>
                    <ChoseOneInput
                        elementState={[course, setCourse]}
                        allElementsLoader={loadCourses}
                        onSelect={() => {}}
                    />
                </div>

                <div>
                    <label className="block text-gray-700 font-medium mb-2">
                        Modalidade
                    </label>
                    <ChoseOneInput
                        elementState={[modality, setModality]}
                        allElementsLoader={loadModalities}
                        onSelect={() => {}}
                    />
                </div>
            </div>

            <div className="flex gap-4 mt-8">
                <Button
                    onClick={handleClose}
                    type="secondary"
                    flexible={true}
                >
                    Cancelar
                </Button>
                <Button
                    onClick={handleCreate}
                    type="primary"
                    flexible={true}
                >
                    Adicionar
                </Button>
            </div>
        </div>

    );
}

export default AmmendmentCreateModal;
