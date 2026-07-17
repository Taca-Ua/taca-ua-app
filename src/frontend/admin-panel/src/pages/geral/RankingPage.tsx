import SeasonSelector from "../../components/seasons/SeasonSelector";
import GeneralRankingListComponent from "../../components/ranking/GeneralRankingListComponent";
import AmmedmentListComponent from "../../components/ranking/AmmedmentListComponent";
import Button from "../../components/utils/Button";
import { useModal } from "../../contexts/ModalContext";
import AmmendmentCreateModal from "../../components/ranking/AmmendmentCreateModal";
import { useState } from "react";

const RankingPage = () => {
    const { pushModal } = useModal();

    const [ammendments, setAmmendments] = useState<any[]>([]);

    return (
        <>
            <SeasonSelector />
            <div className="flex-1 p-8">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-6 flex justify-between items-center">
                        <h1 className="text-3xl font-bold text-gray-800">Ranking</h1>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto">
                <GeneralRankingListComponent />
            </div>

            <div className="max-w-7xl mx-auto mt-8 bg-white p-4 rounded shadow">
                <div className="flex mb-4 justify-end items-center">
                    <Button
                        onClick={() => {pushModal(
                            <AmmendmentCreateModal
                                onCreate={(newAmmendment) => {
                                    setAmmendments((prev) => [newAmmendment, ...prev]);
                                }}
                            />
                        )}}
                        type="primary"
                    >
                        + Adicionar Alteração
                    </Button>
                </div>
                <AmmedmentListComponent ammendmentsState={[ammendments, setAmmendments]} />
            </div>
        </>
    );
};

export default RankingPage;
