import { useState } from 'react';
import NucleusListComponent from '../../components/nucleos/NucleusListComponent';
import NucleoCreateModel from '../../components/nucleos/NucleoCreateModel';
import { type NucleoListItem } from '../../api/nucleos';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';

const Nucleo = () => {

  const createModalController = useState(false);
  const { isAdminGeneral } = useAuth();

  const [nucleus, setNucleus] = useState<NucleoListItem[]>([]);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Núcleos</h1>
            <Button
              onClick={() => createModalController[1](true)}
              type='primary'
              padding='px-6 py-3'
              disabled={!isAdminGeneral}
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

        <NucleoCreateModel
          controller={createModalController}
          onCreate={(newNucleus) => setNucleus([...nucleus, newNucleus])}
        />
      </div>
  );
};

export default Nucleo;
