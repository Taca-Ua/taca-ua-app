import { useEffect, useState } from "react"
import { type CourseListItem, coursesApi } from "../../api/courses"
import { Link } from "react-router"
import { normalizeText } from "../utils/utils"
import LazyImage from "../utils/LazyImage"
import { useNotification } from "../../contexts/NotificationProvider"
import { useSeason } from "../../contexts/SeasonContext"

const CourseEntry = (course: CourseListItem) => {

  const elementIsDisabled = (course.belongs_to_season === undefined)? false : !course.belongs_to_season;

  return (
    <Link
      to={`/cursos/${course.id}`}
      className={"cursor-pointer bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200 p-6 flex flex-col gap-4" + (elementIsDisabled ? " opacity-50" : "")}
    >
      <div className="flex items-center justify-evenly text-center gap-3">
        {course.logo_url ? (
          <LazyImage src={course.logo_url} alt={course.name} className="h-24 object-cover" />
        ) : (
          <div className="w-24 h-24 rounded-full bg-teal-50 flex items-center justify-center border-2 border-teal-500">
            <span className="text-teal-600 font-bold text-sm">{course.abbreviation}</span>
          </div>
        )}
        <div>
          <span className="text-teal-600 font-bold text-lg block">{course.abbreviation}</span>
          <span className="text-gray-800 font-medium text-sm block">{course.name}</span>
        </div>
      </div>
      <div className="pt-2 border-t border-gray-100">
        <span className="text-gray-500 text-xs uppercase tracking-wider">{course.nucleus.name}</span>
      </div>
    </Link>
  )
};

const CoursesListComponent = ( {
  nucleoId,
  coursesState,
} : {
  nucleoId?: string,
  coursesState?: [CourseListItem[] | null, React.Dispatch<React.SetStateAction<CourseListItem[] | null>>]
} ) => {
  const { notify } = useNotification();
  const { loadedSeason } = useSeason();

  const [ courses, setCourses ] = coursesState || useState<CourseListItem[] | null>(null)
  const [loading, setLoading] = useState(true);

  const [ searchQuery, setSearchQuery ] = useState('')
  const [ nucleoFilter, setNucleoFilter ] = useState('')

  useEffect(() => {
    // If courses are already loaded, do not fetch again
    if (courses !== null && courses.length > 0) {
      return;
    }

    setLoading(true)
    coursesApi.getAll(loadedSeason?.id, nucleoId).then(resp => {
      setCourses(resp)
    }).catch(() => {
      notify('Erro ao carregar cursos', 'error')
    }).finally(() => {
      setLoading(false)
    })
  }, [])

  const filteredCourses =
    courses?.filter(
      (c) =>
        (normalizeText(c.name).includes(normalizeText(searchQuery)) ||
          normalizeText(c.abbreviation).includes(normalizeText(searchQuery)) ||
          normalizeText(c.nucleus.name).includes(normalizeText(searchQuery))) &&
        (nucleoFilter === "" || c.nucleus.id === nucleoFilter),
    ) || [];
  const sortedCourses = filteredCourses
    .sort((a, b) => a.name.localeCompare(b.name))
    .sort((a) => (a.belongs_to_season ? -1 : 1));

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center py-8">Carregando cursos...</p>
      </div>
    )
  }

  if (!courses) {
    return (
      <div className="bg-red-50 rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center py-8">Erro ao carregar cursos.</p>
      </div>
    )
  }

  if (courses.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center py-8">Nenhum curso disponível.</p>
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
          {[... new Map(courses.map(c => [c.nucleus.id, c.nucleus])).values()]
          .sort((a, b) => a.name.localeCompare(b.name)).map(n => (
            <option key={`select-${n.id}`} value={n.id}>{n.name}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedCourses.length > 0 ? (
          sortedCourses
            .map((course) => (
              <CourseEntry key={course.id} {...course} />
            ))
        ) : (
          <p className="text-gray-500 text-center py-8 col-span-full">
            Nenhum curso encontrado.
          </p>
        )}
      </div>
    </div>
  );
}

export default CoursesListComponent
