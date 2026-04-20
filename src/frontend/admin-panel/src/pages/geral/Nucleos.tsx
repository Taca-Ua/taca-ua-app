import { useState } from 'react';
import { btn } from '../../styles/buttonStyles';
import NucleusListComponent from '../../components/nucleos/NucleusListComponent';
import NucleoCreateModel from '../../components/nucleos/NucleoCreateModel';
import { type NucleoListItem } from '../../api/nucleos';

const Nucleo = () => {

  const createModalController = useState(false);
  const [nucleus, setNucleus] = useState<NucleoListItem[]>([]);

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Núcleos</h1>
            <button
              onClick={() => createModalController[1](true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2`}
            >
              <span>+</span>
              Adicionar Núcleo
            </button>
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
