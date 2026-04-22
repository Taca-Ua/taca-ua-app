import { useEffect, useState } from 'react';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../utils/Button';
import ModalityEditModal from './ModalityEditModel';


const ModalityDetailComponent = ( {modalityId} : { modalityId: string }) => {
  const navigate = useNavigate();
  const { isAdminGeneral } = useAuth();

  const [modality, setModality] = useState<ModalityDetail | null>(null);

  const editModalController = useState(false);

  useEffect(() => {
    const fetchModality = async () => {
      try {
        const data = await modalitiesApi.getById(modalityId);
        setModality(data);
      } catch (error) {
        console.error('Error fetching modality detail:', error);
      }
    };

    fetchModality();
  }, []);

  const handleDelete = async () => {
    try {
      await modalitiesApi.delete(modalityId);
      navigate('/geral/modalidades');
    } catch (error) {
      console.error('Error deleting modality:', error);
    }
  };

  if (!modality) {
    return <div className="text-gray-500">Carregando detalhes da modalidade...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8 mb-6">
      <div className="space-y-6">
        <div>
          <label className="block text-teal-500 font-medium mb-2">Nome</label>
          <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800">
            {modality.name}
          </div>
        </div>
        <div>
          <label className="block text-teal-500 font-medium mb-2">Tipo</label>
          <div className="bg-gray-100 px-4 py-3 rounded-md text-gray-800 capitalize">
            {modality.modality_type.name}
          </div>
        </div>
      </div>

      <div className="flex gap-4 mt-8">
        <Button
          onClick={() => editModalController[1](true)}
          type="primary"
          active={isAdminGeneral}
          flexible={true}
        >
          Editar
        </Button>
        <Button
          onClick={handleDelete}
          type="danger"
          active={isAdminGeneral}
          confirmation={{
            title: 'Eliminar modalidade',
            message: 'Tem certeza que deseja eliminar esta modalidade?',
            confirmLabel: 'Eliminar',
          }}
          flexible={true}
        >
          Eliminar
        </Button>
      </div>

      <ModalityEditModal
        controller={editModalController}
        modalityState={[modality, setModality]}
      />
    </div>
  );
};

export default ModalityDetailComponent;
