import { useEffect, useState } from 'react';
import { btn } from '../../styles/buttonStyles';
import { modalitiesApi, type ModalityDetail } from '../../api/modalities';
import ConfirmModal from '../ConfirmModal';
import ModalityEditModel from './ModalityEditModel';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';


const ModalityDetailComponent = ( {modalityId} : { modalityId: string }) => {
  const navigate = useNavigate();
  const { isAdminGeneral } = useAuth();

  const [modality, setModality] = useState<ModalityDetail | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
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
    setDeleting(true);
    try {
      await modalitiesApi.delete(modalityId);
      navigate('/geral/modalidades');
    } catch (error) {
      console.error('Error deleting modality:', error);
    } finally {
      setDeleting(false);
      setIsDeleteModalOpen(false);
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
        <button
          onClick={() => editModalController[1](true)}
          className={`flex-1 px-6 py-3 ${btn.primary} rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-teal-400 disabled:opacity-50 disabled:cursor-not-allowed`}
          disabled={!isAdminGeneral}
        >
          Editar
        </button>
        <button
          onClick={() => setIsDeleteModalOpen(true)}
          className={`flex-1 px-6 py-3 ${btn.danger} rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-red-400 disabled:opacity-50 disabled:cursor-not-allowed`}
          disabled={!isAdminGeneral}
        >
          Eliminar
        </button>
      </div>

      <ModalityEditModel
        controller={editModalController}
        onSave={(updatedModality) => {
          setModality(updatedModality);
        }}
        modalityData={modality}
      />

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        title="Eliminar modalidade"
        message="Tem certeza que deseja eliminar esta modalidade?"
        confirmLabel="Eliminar"
        variant="danger"
        loading={deleting}
        onCancel={() => {
          if (!deleting) {
            setIsDeleteModalOpen(false);
          }
        }}
        onConfirm={handleDelete}
      />
    </div>
  );
};

export default ModalityDetailComponent;
