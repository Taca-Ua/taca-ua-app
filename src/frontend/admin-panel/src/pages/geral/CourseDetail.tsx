import { useNavigate, useParams } from 'react-router-dom';
import CourseInfoComponent from '../../components/courses/CourseInfoComponent';
import Button from '../../components/utils/Button';
import { navigateBack } from '../../utils';
import { coursesApi, type CourseDetail } from '../../api/courses';
import { useEffect, useState } from 'react';
import { useSeason } from '../../contexts/SeasonContext';
import SeasonSelector from '../../components/seasons/SeasonSelector';
import TabSystem from '../../components/TabSystem';
import MatchesCalendarComponent from '../../components/matches/MatchesCalendarComponent';

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

  if (!course) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Carregando detalhes do curso...</p>
      </div>
    );
  }

  return (
    <>
      <SeasonSelector relevantSeasonIds={course.relevant_season_ids || []} />
      <div className="flex-1 p-8 max-w-5xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">
            Detalhes do Curso
          </h1>
          <div>
            <Button onClick={handleBack} type="secondary" padding="px-6 py-3">
              Voltar
            </Button>
          </div>
        </div>

        <CourseInfoComponent courseState={[course, setCourse]} />
      </div>
    </>
  );
};

export default CursoDetail;
