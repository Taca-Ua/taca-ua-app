import { useState } from 'react';
import NucleusListComponent from '../../components/nucleos/NucleusListComponent';
import NucleoCreateModal from '../../components/nucleos/NucleoCreateModal';
import { type NucleoListItem } from '../../api/nucleos';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';

const Nucleo = () => {

  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();

  const [nucleus, setNucleus] = useState<NucleoListItem[]>([]);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Núcleos</h1>
            <Button
              onClick={() => pushModal(
                <NucleoCreateModal
                  onCreate={(newNucleus) => setNucleus([...nucleus, newNucleus])}
                />
              )}
              type='primary'
              padding='px-6 py-3'
              active={isAdminGeneral}
            >
              + Adicionar Núcleo
            </Button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <NucleusListComponent
              nucleosState={[nucleus, setNucleus]}
            />
          </div>
        </div>
      </div>
  );
};

export default Nucleo;
