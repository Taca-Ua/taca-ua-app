import { useNavigate, useParams } from 'react-router-dom';
import { btn } from '../../styles/buttonStyles';
import NucleusDetailComponent from '../../components/nucleos/NucleusDetailComponent';

const NucleoDetails = () => {
  const navigate = useNavigate();
  const nucleusId = useParams<{ id: string }>().id;
  if (!nucleusId) {
    navigate('/geral/nucleos');
    return null;
  }

  return (
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Núcleo</h1>
            <button
              onClick={() => navigate('/geral/nucleos')}
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
            >
              Voltar
            </button>
          </div>

          {/* Nucleus Detail Component */}
          <NucleusDetailComponent nucleusId={nucleusId} />
        </div>
      </div>
  );
};

export default NucleoDetails;
