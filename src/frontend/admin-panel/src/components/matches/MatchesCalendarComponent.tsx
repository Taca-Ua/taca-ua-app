import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { matchesApi, type MatchListItem } from "../../api/matches";

const MatchesCalendarComponent = ({
  courseId,
  modalityId,
} : {
  courseId?: string;
  modalityId?: string;
}) => {

    const navigate = useNavigate();

    const [matches, setMatches] = useState<MatchListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [selectedDay, setSelectedDay] = useState(new Date());
    const [dayPage, setDayPage] = useState(1);

    const monthName = currentMonth.toLocaleDateString("pt-PT", { month: "long", year: "numeric" });

    useEffect(() => {
        setLoading(true);
        matchesApi.getAll({
            date_from: new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).toISOString().split("T")[0],
            date_to: new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).toISOString().split("T")[0],
            course_id: courseId,
            modality_id: modalityId,
        }).then((data) => {
            setMatches(data.matches);
        }).catch((err) => {
            console.error("Erro ao carregar jogos:", err);
        }).finally(() => {
            setLoading(false);
        });
    }, [currentMonth]);

    const getStatusDotColor = (status: string) => {
        switch (status) {
            case "scheduled":
                return "bg-blue-500";
            case "in_progress":
                return "bg-amber-500";
            case "finished":
                return "bg-green-500";
            case "cancelled":
                return "bg-red-400";
            default:
                return "bg-gray-300";
        }
    };

    const getStatusDisplay = (status: string) => {
        switch (status) {
            case "scheduled":
                return "Agendado";
            case "in_progress":
                return "Em curso";
            case "finished":
                return "Terminado";
            case "cancelled":
                return "Cancelado";
            default:
                return status;
        }
    };

    const getDaysInMonth = (date: Date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        return {
            daysInMonth: lastDay.getDate(),
            startingDayOfWeek: firstDay.getDay(),
        };
    };

    const getMatchesForDay = (day: number) => {
        return matches.filter((m) => {
            const d = new Date(m.start_time);
            return (
                d.getDate() === day &&
                d.getMonth() === currentMonth.getMonth() &&
                d.getFullYear() === currentMonth.getFullYear()
            );
        });
    };

    const previousMonth = () => {
        setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    };

    const nextMonth = () => {
        setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    };

    const formatDateTime = (isoString: string) => {
        const date = new Date(isoString);
        return {
            time: date.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" }),
            date: date.toLocaleDateString("pt-PT"),
        };
    };

    return (
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Calendar Grid */}
        <div className="lg:w-3/5 h-full bg-white rounded-lg shadow-md overflow-hidden">
          <div className="flex justify-between items-center px-6 py-4 bg-gray-50 border-b">
            <button
              onClick={previousMonth}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md font-medium transition-colors"
            >
              ←
            </button>
            <h2 className="text-xl font-bold text-gray-800 capitalize">
              {monthName}
            </h2>
            <button
              onClick={nextMonth}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md font-medium transition-colors"
            >
              →
            </button>
          </div>

          <div className="p-4">
            <div className="grid grid-cols-7 mb-2">
              {["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"].map((day) => (
                <div
                  key={day}
                  className="text-center text-sm font-semibold text-gray-600 py-2"
                >
                  {day}
                </div>
              ))}
            </div>
            <div
              className={
                `grid grid-cols-7 gap-1` + (loading ? " opacity-30" : "")
              }
            >
              {(() => {
                const { daysInMonth, startingDayOfWeek } =
                  getDaysInMonth(currentMonth);
                const cells = [];
                for (let i = 0; i < startingDayOfWeek; i++) {
                  cells.push(<div key={`empty-start-${i}`} />);
                }
                for (let day = 1; day <= daysInMonth; day++) {
                  const isToday = new Date();
                  const isTodayDay =
                    day === isToday.getDate() &&
                    currentMonth.getMonth() === isToday.getMonth() &&
                    currentMonth.getFullYear() === isToday.getFullYear();
                  const isSelected =
                    day === selectedDay.getDate() &&
                    currentMonth.getMonth() === selectedDay.getMonth() &&
                    currentMonth.getFullYear() === selectedDay.getFullYear();

                  const matchesForDay = getMatchesForDay(day);
                  const scheduledCount = matchesForDay.filter(
                    (m) => m.status === "scheduled",
                  ).length;
                  const inProgressCount = matchesForDay.filter(
                    (m) => m.status === "in_progress",
                  ).length;
                  const finishedCount = matchesForDay.filter(
                    (m) => m.status === "finished",
                  ).length;
                  const cancelledCount = matchesForDay.filter(
                    (m) => m.status === "cancelled",
                  ).length;

                  cells.push(
                    <button
                      key={day}
                      onClick={() => {
                        setSelectedDay(
                          new Date(
                            currentMonth.getFullYear(),
                            currentMonth.getMonth(),
                            day,
                          ),
                        );
                        setDayPage(1);
                      }}
                      className={`aspect-square flex flex-col items-center justify-center rounded-lg border-2 transition-colors ${
                        isSelected
                          ? "border-teal-500 bg-teal-50"
                          : isTodayDay
                            ? "border-teal-200 bg-teal-50/50 hover:border-teal-400"
                            : "border-transparent hover:border-gray-300 bg-white"
                      }`}
                    >
                      <span>{day}</span>
                      <div className="flex mt-1 gap-0.5">
                        {scheduledCount > 0 && (
                          <span
                            className={`w-2 h-2 rounded-full ${getStatusDotColor("scheduled")}`}
                          ></span>
                        )}
                        {inProgressCount > 0 && (
                          <span
                            className={`w-2 h-2 rounded-full ${getStatusDotColor("in_progress")}`}
                          ></span>
                        )}
                        {finishedCount > 0 && (
                          <span
                            className={`w-2 h-2 rounded-full ${getStatusDotColor("finished")}`}
                          ></span>
                        )}
                        {cancelledCount > 0 && (
                          <span
                            className={`w-2 h-2 rounded-full ${getStatusDotColor("cancelled")}`}
                          ></span>
                        )}
                      </div>
                    </button>,
                  );
                }
                return cells;
              })()}
            </div>
          </div>

          {/* Legend */}
          <div className="px-6 py-3 bg-gray-50 border-t flex flex-wrap items-center gap-4 text-xs text-gray-600">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
              Agendado
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block"></span>
              Em curso
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
              Terminado
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-400 inline-block"></span>
              Cancelado
            </span>
          </div>
        </div>

        {/* Side Panel */}
        <div className="lg:w-2/5">
          <div className="bg-white rounded-lg shadow-md p-5 sticky top-4">
            <h3 className="text-lg font-bold text-gray-800 mb-1 capitalize">
              {selectedDay.toLocaleDateString("pt-PT", {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </h3>
            {(() => {
              const dayMatches = matches.filter((m) => {
                const d = new Date(m.start_time);
                return (
                  d.getDate() === selectedDay.getDate() &&
                  d.getMonth() === selectedDay.getMonth() &&
                  d.getFullYear() === selectedDay.getFullYear()
                );
              });
              const GAMES_PER_PAGE = 10;
              const totalDayPages = Math.ceil(
                dayMatches.length / GAMES_PER_PAGE,
              );
              const paginated = dayMatches.slice(
                (dayPage - 1) * GAMES_PER_PAGE,
                dayPage * GAMES_PER_PAGE,
              );
              if (dayMatches.length === 0) {
                return (
                  <p className="text-gray-500 text-sm py-6 text-center">
                    Não há jogos neste dia.
                  </p>
                );
              }
              return (
                <>
                  <p className="text-sm text-gray-500 mb-3">
                    {dayMatches.length} jogo{dayMatches.length !== 1 ? "s" : ""}
                  </p>
                  <div className="space-y-2 overflow-y-auto">
                    {paginated.map((match) => {
                      const { time } = formatDateTime(match.start_time);
                      return (
                        <button
                          key={match.id}
                          type="button"
                          onClick={() => navigate(`/jogos/${match.id}`)}
                          className="w-full text-left p-3 bg-gray-50 rounded-lg hover:bg-teal-50 transition-colors border border-transparent hover:border-teal-200"
                        >
                          <div className="flex justify-between items-start mb-1">
                            <span className="font-semibold text-sm text-gray-800">
                              {time}
                            </span>
                            <span
                              className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                                match.status === "scheduled"
                                  ? "bg-blue-100 text-blue-700"
                                  : match.status === "in_progress"
                                    ? "bg-amber-100 text-amber-700"
                                    : match.status === "finished"
                                      ? "bg-green-100 text-green-700"
                                      : "bg-red-100 text-red-700"
                              }`}
                            >
                              {getStatusDisplay(match.status)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700">
                            {match.participants
                              .map((p) => p.name || "TBD")
                              .join(" vs ")}
                          </p>
                          {match.tournament && (
                            <p className="text-xs text-teal-600 mt-0.5">
                              {match.tournament.name}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 mt-0.5">
                            {match.location}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                  {totalDayPages > 1 && (
                    <div className="mt-4 flex justify-between items-center">
                      <button
                        onClick={() => setDayPage((p) => Math.max(1, p - 1))}
                        disabled={dayPage === 1}
                        className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Anterior
                      </button>
                      <span className="text-sm text-gray-600">
                        {dayPage} / {totalDayPages}
                      </span>
                      <button
                        onClick={() =>
                          setDayPage((p) => Math.min(totalDayPages, p + 1))
                        }
                        disabled={dayPage === totalDayPages}
                        className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Próxima
                      </button>
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      </div>
    );
};

export default MatchesCalendarComponent;
