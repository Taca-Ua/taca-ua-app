import { useNavigate, useParams } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

import { btn } from '../../styles/buttonStyles';
import CourseDetailComponent from '../../components/courses/CourseDetailComponent';

const CursoDetail = () => {
  const navigate = useNavigate();
  const courseId = useParams<{ id: string }>().id;
  if (!courseId) {
    navigate('/geral/cursos');
    return null;
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Detalhes do Curso</h1>
            <button
              onClick={() => navigate('/geral/cursos')}
              className={`px-6 py-3 ${btn.secondary} rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400`}
            >
              Voltar
            </button>
          </div>

          <CourseDetailComponent courseId={courseId} />
        </div>
      </div>
    </div>
  );
};

export default CursoDetail;
