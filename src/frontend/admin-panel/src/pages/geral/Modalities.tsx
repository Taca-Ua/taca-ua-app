import { useState } from "react";
import { type ModalityListItem } from "../../api/modalities";
import ModalitiesListComponent from "../../components/modalities/ModalitiesListComponent";
import ModalityCreateModel from "../../components/modalities/ModalityCreateModel";
import { useAuth } from "../../hooks/useAuth";
import Button from "../../components/utils/Button";



const Modalities = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { isAdminGeneral } = useAuth();

  const modalitiesState = useState<ModalityListItem[]>([]);
  const [modalityTypes, setModalityTypes] = modalitiesState;  // Desestruturação para obter o estado e a função de atualização

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Modalidades ({modalityTypes.length})</h1>
            <div>
              <Button
                onClick={() => setIsModalOpen(true)}
                type='primary'
                active={isAdminGeneral}
              >
                + Adicionar Modalidade
              </Button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <ModalitiesListComponent
              modalitiesState={modalitiesState}
            />
          </div>
        </div>

        {isModalOpen && (
          <ModalityCreateModel
            onCreate={(newModality) => {
              setModalityTypes((prev) => [...prev, newModality]);
              setIsModalOpen(false);
            }}
            onClose={() => setIsModalOpen(false)}
          />
        )}
      </div>
  );
};

export default Modalities;
