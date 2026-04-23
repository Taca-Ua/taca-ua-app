import { useNavigate, useParams } from 'react-router-dom';

import CourseDetailComponent from '../../components/courses/CourseDetailComponent';
import Button from '../../components/utils/Button';

const CursoDetail = () => {
  const navigate = useNavigate();
  const courseId = useParams<{ id: string }>().id;
  if (!courseId) {
    navigate('/cursos');
    return null;
  }

  return (
    <div className="flex-1 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes do Curso</h1>
          <div>
            <Button
              onClick={() => navigate(`/cursos/`)}
              type='secondary'
              padding='px-6 py-3'
            >
              Voltar
            </Button>
          </div>
        </div>

        <CourseDetailComponent courseId={courseId} />
      </div>
    </div>
  );
};

export default CursoDetail;
