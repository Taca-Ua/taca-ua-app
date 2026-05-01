import { useEffect, useState } from 'react';
import { type CourseListItem, coursesApi } from '../../api/courses';
import CoursesListComponent from '../../components/courses/CoursesListComponent';
import CourseCreateModal from '../../components/courses/CourseCreateModal';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import { useNotification } from '../../contexts/NotificationProvider';
import { useSeason } from '../../contexts/SeasonContext';


const Cursos = () => {
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();
  const { notify } = useNotification();
  const [ isLoading, setIsLoading ] = useState(true);
  const { currentSeason } = useSeason();

  const [courses, setCourses] = useState<CourseListItem[] | null>(null);  // Estado para armazenar os cursos

  useEffect(() => {
    setIsLoading(true);
    coursesApi.getAll(currentSeason?.id).then(data => {
      setCourses(data);
    }).catch(err => {
      console.error("Failed to fetch courses:", err);
      notify("Erro ao carregar cursos", "error");
      setCourses([]);
    }).finally(() => {
      setIsLoading(false);
    });
  }, [currentSeason?.id]);  // Carrega os cursos ao montar o componente

  if (isLoading) {
    return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-500 text-center py-8">Carregando cursos...</p>
          </div>
        </div>
      </div>
    );
  }

  if (courses === null) {
    return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-500 text-center py-8">Nenhum curso encontrado.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <div>
              <Button
                onClick={() => pushModal(<CourseCreateModal onCreate={(newCourse) => setCourses([...courses, newCourse])} />)}
                type='primary'
                active={isAdminGeneral}
              >
                + Adicionar Curso
              </Button>
            </div>
          </div>

          <CoursesListComponent coursesState={[courses, setCourses]} />
        </div>
      </div>
  );
};

export default Cursos;
