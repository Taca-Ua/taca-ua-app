import { useNavigate, useParams } from 'react-router-dom';
import NucleusDetailComponent from '../../components/nucleos/NucleusDetailComponent';
import Button from '../../components/utils/Button';
import TabSystem from '../../components/TabSystem';
import CoursesListComponent from '../../components/courses/CoursesListComponent';

const NucleoDetails = () => {
  const navigate = useNavigate();
  const nucleusId = useParams<{ id: string }>().id;
  if (!nucleusId) {
    navigate('/nucleos');
    return null;
  }

  return (
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto mb-8">
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

        <TabSystem
          elements={[
            {
              id: 'courses',
              label: 'Cursos',
              content: <CoursesListComponent nucleoId={nucleusId} />
            },
            {
              id: 'teams',
              label: 'Equipas',
              content: <div className="p-4">Conteúdo das equipas do núcleo (a ser implementado)</div>
            },
            {
              id: 'matches',
              label: 'Jogos',
              content: <div className="p-4">Conteúdo dos jogos do núcleo (a ser implementado)</div>
            }
          ]}
        />
      </div>
  );
};

export default NucleoDetails;
