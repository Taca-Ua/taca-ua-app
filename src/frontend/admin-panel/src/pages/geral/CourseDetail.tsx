import { useNavigate, useParams } from 'react-router-dom';
import CourseInfoComponent from '../../components/courses/CourseInfoComponent';
import Button from '../../components/utils/Button';
import { navigateBack } from '../../utils';
import { coursesApi, type CourseDetail } from '../../api/courses';
import { useEffect, useState } from 'react';
import { useSeason } from '../../contexts/SeasonContext';

const CursoDetail = () => {
  const courseId = useParams<{ id: string }>().id;
  const navigate = useNavigate();
  const { loadedSeason } = useSeason();

  const [course, setCourse] = useState<CourseDetail | null>(null);

  useEffect(() => {
    if (!courseId) return;
    coursesApi.getById(courseId, loadedSeason?.id)
      .then(setCourse)
      .catch((error) => {
        console.error("Erro ao carregar detalhes do curso:", error);
      });

  }, [courseId, loadedSeason?.id]);

  const handleBack = () => {
    navigateBack(navigate, '/cursos');
  };

  if (!courseId) {
    handleBack();
    return null;
  }

  return (
    <div className="flex-1 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Detalhes do Curso</h1>
          <div>
            <Button
              onClick={handleBack}
              type='secondary'
              padding='px-6 py-3'
            >
              Voltar
            </Button>
          </div>
        </div>

        <CourseInfoComponent courseState={[course, setCourse]} />
      </div>
    </div>
  );
};

export default CursoDetail;
