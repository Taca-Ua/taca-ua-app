import { useNavigate, useParams } from 'react-router-dom';
import NucleusDetailComponent from '../../components/nucleos/NucleusDetailComponent';
import Button from '../../components/utils/Button';

const NucleoDetails = () => {
  const navigate = useNavigate();
  const nucleusId = useParams<{ id: string }>().id;
  if (!nucleusId) {
    navigate('/nucleos');
    return null;
  }

  return (
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Núcleo</h1>
            <Button
              onClick={() => navigate('/nucleos')}
              type='secondary'
              padding='px-6 py-3'
            >
              Voltar
            </Button>
          </div>

          {/* Nucleus Detail Component */}
          <NucleusDetailComponent nucleusId={nucleusId} />
        </div>
      </div>
  );
};

export default NucleoDetails;
