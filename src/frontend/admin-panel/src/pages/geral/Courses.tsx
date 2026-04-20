import { useState } from 'react';
import { type CourseListItem } from '../../api/courses';
import { btn } from '../../styles/buttonStyles';
import CoursesListComponent from '../../components/courses/CoursesListComponent';
import CourseCreateModel from '../../components/courses/CourseCreateModel';
import { useAuth } from '../../hooks/useAuth';


const Cursos = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { isAdminGeneral } = useAuth();

  const [courses, setCourses] = useState<CourseListItem[]>([]);  // Estado para armazenar os cursos

  return (
      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed`}
              disabled={!isAdminGeneral}
            >
              <span>+</span>
              Adicionar Curso
            </button>
          </div>

          <CoursesListComponent coursesState={[courses, setCourses]} />
        </div>
        <CourseCreateModel
          controller={[isModalOpen, setIsModalOpen]}
          onCreate={(newCourse) => setCourses([...courses, newCourse])}
        />
      </div>
  );
};

export default Cursos;
