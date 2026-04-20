import { useState } from "react";
import { type ModalityListItem } from "../../api/modalities";
import { btn } from '../../styles/buttonStyles';
import ModalitiesListComponent from "../../components/modalities/ModalitiesListComponent";
import ModalityCreateModel from "../../components/modalities/ModalityCreateModel";
import { useAuth } from "../../hooks/useAuth";



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
            <button
              onClick={() => setIsModalOpen(true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed`}
              disabled={!isAdminGeneral}
            >
              <span>+</span>
              Adicionar Modalidade
            </button>
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
