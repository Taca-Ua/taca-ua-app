import { useState } from 'react';
import { type CourseListItem } from '../../api/courses';
import CoursesListComponent from '../../components/courses/CoursesListComponent';
import CourseCreateModal from '../../components/courses/CourseCreateModal';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/utils/Button';


const Cursos = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { isAdminGeneral } = useAuth();

  const [courses, setCourses] = useState<CourseListItem[]>([]);  // Estado para armazenar os cursos

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <div>
              <Button
                onClick={() => setIsModalOpen(true)}
                type='primary'
                active={isAdminGeneral}
              >
                + Adicionar Curso
              </Button>
            </div>
          </div>

          <CoursesListComponent coursesState={[courses, setCourses]} />
        </div>
        <CourseCreateModal
          controller={[isModalOpen, setIsModalOpen]}
          onCreate={(newCourse) => setCourses([...courses, newCourse])}
        />
      </div>
  );
};

export default Cursos;
