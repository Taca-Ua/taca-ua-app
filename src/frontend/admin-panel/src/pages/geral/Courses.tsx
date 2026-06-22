import { useState } from 'react';
import { type CourseListItem } from '../../api/courses';
import CoursesListComponent from '../../components/courses/CoursesListComponent';
import CourseCreateModal from '../../components/courses/CourseCreateModal';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';
import { useModal } from '../../contexts/ModalContext';
import { useNavigate } from 'react-router-dom';
import SeasonSelector from '../../components/seasons/SeasonSelector';


const Cursos = () => {
  const { isAdminGeneral } = useAuth();
  const { pushModal } = useModal();
  const navigate = useNavigate();

  // Store state for courses
  const [courses, setCourses] = useState<CourseListItem[] | null>(null);

  return (
    <>
      <SeasonSelector />
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <div>
              <Button
                onClick={() => pushModal(
                  <CourseCreateModal
                    onCreate={(newCourse) => navigate(`/cursos/${newCourse.id}`)}
                  />
                )}
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
    </>
  );
};

export default Cursos;
