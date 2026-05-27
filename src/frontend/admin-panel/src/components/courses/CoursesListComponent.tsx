import { useState } from "react"
import { type CourseListItem } from "../../api/courses"
import { useNavigate } from "react-router"

const CourseEntry = (course: CourseListItem) => {
  const navigate = useNavigate();
  return (
    <button
      type="button"
      onClick={() => navigate(`/cursos/${course.id}`)}
      className={"w-full text-left px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors flex justify-between items-center focus:outline-none focus:ring-2 focus:ring-teal-500" + (course.belongs_to_season ? "" : " opacity-50")}
    >
      <div className="flex items-center gap-4">
        {course.logo_url ? (
          <img src={course.logo_url} alt={course.name} className="w-12 h-12 rounded-full object-cover" />
        ) : (
          <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center border-2 border-teal-500 flex-shrink-0">
            <span className="text-teal-600 font-bold text-xs">{course.abbreviation}</span>
          </div>
        )}
        <div className="flex items-center gap-3">
          <span className="text-teal-600 font-bold text-lg">{course.abbreviation}</span>
          <span className="text-gray-400">|</span>
          <span className="text-gray-800 font-medium">{course.name}</span>
        </div>
      </div>
      <span className="text-gray-500 text-sm">{course.nucleo.name}</span>
    </button>
  )
};

const CoursesListComponent = ( {
  coursesState,
} : {
  coursesState: [CourseListItem[], React.Dispatch<React.SetStateAction<CourseListItem[] | null>>]
} ) => {
  const [ courses, ] = coursesState

  const [ searchQuery, setSearchQuery ] = useState('')
  const [ nucleoFilter, setNucleoFilter ] = useState('')

  const filteredCourses = courses?.filter(c =>
    (c.name.toLowerCase().includes(searchQuery.toLowerCase()) || c.abbreviation.toLowerCase().includes(searchQuery.toLowerCase())) &&
    (nucleoFilter === '' || c.nucleo.id === nucleoFilter)
  ) || []
  const sortedCourses = filteredCourses.sort((a, b) => a.name.localeCompare(b.name)).sort((a) => a.belongs_to_season? -1 : 1)

  if (courses === null) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center py-8">Carregando cursos...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6 flex gap-3">
        <input
          type="text"
          placeholder="Pesquisar curso..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
        />
        <select
          value={nucleoFilter}
          onChange={(e) => setNucleoFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
        >
          <option value="">Todos os núcleos</option>
          {[... new Map(courses.map(c => [c.nucleo.id, c.nucleo])).values()]
          .sort((a, b) => a.name.localeCompare(b.name)).map(n => (
            <option key={`select-${n.id}`} value={n.id}>{n.name}</option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        {sortedCourses.length > 0 ? (
          sortedCourses
            .map((course) => (
              <CourseEntry key={course.id} {...course} />
            ))
        ) : (
          <p className="text-gray-500 text-center py-8">
            Nenhum curso encontrado.
          </p>
        )}
      </div>
    </div>
  );
}

export default CoursesListComponent
