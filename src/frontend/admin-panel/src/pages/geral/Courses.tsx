import { useState } from 'react';
import Sidebar from '../../components/geral_navbar';
import { type CourseListItem } from '../../api/courses';
import { btn } from '../../styles/buttonStyles';
import CoursesListComponent from '../../components/courses/CoursesListComponent';
import CourseCreateModel from '../../components/courses/CourseCreateModel';


const Cursos = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [courses, setCourses] = useState<CourseListItem[]>([]);  // Estado para armazenar os cursos

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Cursos</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className={`px-6 py-3 ${btn.primary} rounded-md font-medium transition-colors flex items-center gap-2`}
            >
              <span>+</span>
              Adicionar Curso
            </button>
          </div>

          <CoursesListComponent coursesState={[courses, setCourses]} />
        </div>
      </div>

      <CourseCreateModel
        controller={[isModalOpen, setIsModalOpen]}
        onCreate={(newCourse) => setCourses([...courses, newCourse])}
      />
    </div>
  );
};

export default Cursos;
