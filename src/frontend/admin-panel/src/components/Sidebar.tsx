import { Link } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useModal } from "../contexts/ModalContext";
import { useSeason } from "../contexts/SeasonContext";
import LazyImage from "./utils/LazyImage";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isChangingSeason, setIsChangingSeason] = useState(false);
  const { logout, username } = useAuth();
  const { clearModals } = useModal();
  const { availableSeasons, loadedSeason, selectSeason } = useSeason();

  const navItems = [
    // system management
    [{ to: "/administradores", label: "Administradores", short: "Adm" },
      { to: "/public-website-config", label: "Configuração do Site Público", short: "CSP" },
    ],

    // modalities management
    [{ to: "/formatos-prova", label: "Formatos de Prova", short: "FP" },
    { to: "/modalidades", label: "Modalidades", short: "Mod" },
    { to: "/regulamentos", label: "Regulamentos", short: "Reg" },],

    // academic structure
    [{ to: "/nucleos", label: "Núcleos", short: "Núc" },
    { to: "/cursos", label: "Cursos", short: "Cur" },
    { to: "/equipas", label: "Equipas", short: "Equ" },
          { to: "/membros", label: "Membros", short: "Mem" },],

    // tournaments management
    [{ to: "/torneios", label: "Torneios", short: "Tor" },
    { to: "/jogos", label: "Jogos", short: "Jog" },],
  ];

  const handlePageChange = () => {
    clearModals();
    setIsOpen(false);
  };

  const handleSeasonChange = async (seasonId: number) => {
    try {
      setIsChangingSeason(true);
      const selectedSeason = availableSeasons.find(s => s.id === seasonId);
      if (!selectedSeason) throw new Error("Selected season not found");
      selectSeason(selectedSeason);
    } catch (error) {
      console.error("Failed to change season:", error);
      setIsChangingSeason(false);
    } finally {
      setIsChangingSeason(false);
    }
  };

  return (
    <>
      <aside
        className={`fixed top-0 left-0 h-screen bg-white shadow-xl border-r border-gray-200 z-50 transition-all duration-300 flex flex-col ${isOpen ? "w-64" : "w-16"}`}
      >
        <div className="flex flex-col h-full">
          <div className="flex flex-col flex-1 min-h-0">
            <div className="flex items-center justify-between border-b border-gray-200 h-16 flex-shrink-0 px-3">
              {isOpen ? (
                <>
                  <Link
                    to="/dashboard"
                    className="flex items-center gap-2 min-w-0 text-lg font-bold text-teal-600 hover:text-teal-700"
                    onClick={handlePageChange}
                  >
                    <LazyImage
                      src="/logo.png"
                      alt="TaçaUA"
                      className="h-8 w-8 object-contain flex-shrink-0"
                    />
                    <span className="truncate">TaçaUA</span>
                  </Link>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-gray-500 hover:text-red-500 transition ml-2 flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-teal-400 rounded"
                    aria-label="Fechar menu"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsOpen(true)}
                  className="w-full flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-teal-600 transition focus:outline-none focus:ring-2 focus:ring-teal-400 rounded"
                  aria-label="Abrir menu"
                >
                  <span className="block w-5 h-0.5 bg-current"></span>
                  <span className="block w-5 h-0.5 bg-current"></span>
                  <span className="block w-5 h-0.5 bg-current"></span>
                </button>
              )}
            </div>

            {/* Season Selector */}
            {availableSeasons.length > 0 && (
              <div className="border-b border-gray-200 px-3 py-3">
                <label className={`text-xs font-semibold text-gray-600 block mb-2 ${!isOpen && "sr-only"}`}>
                  Época
                </label>
                <select
                  value={loadedSeason?.id || ""}
                  onChange={(e) => handleSeasonChange(Number(e.target.value))}
                  disabled={isChangingSeason}
                  className="w-full px-2 py-2 text-sm border border-gray-300 rounded text-gray-700 hover:border-teal-400 focus:outline-none focus:ring-2 focus:ring-teal-400 disabled:opacity-50 disabled:cursor-not-allowed"
                  title={!isOpen ? `${loadedSeason?.name}` : undefined}
                >
                  {availableSeasons.sort((a, b) => b.id - a.id).map((season) => (
                    <option key={season.id} value={season.id}>
                      {season.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="overflow-y-auto flex-1 min-h-0">
            {
              // Render nav items in groups with separators
              navItems.map((group, index) => (
                <div key={index}>
                  <nav className="flex-1 py-2">
                    {group.map((item) => (
                      <Link
                        key={item.to}
                        to={item.to}
                        onClick={handlePageChange}
                        className="flex items-center h-11 px-3 text-gray-700 hover:text-teal-600 hover:bg-teal-50 transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-teal-400"
                        title={!isOpen ? item.label : undefined}
                      >
                        {isOpen ? (
                          <span className="font-medium truncate">
                            {item.label}
                          </span>
                        ) : (
                          <span className="text-xs font-bold w-full text-center">
                            {item.short}
                          </span>
                        )}
                      </Link>
                    ))}
                  </nav>
                  {index < navItems.length - 1 && (
                    <div className="border-t border-gray-200" />
                  )}
                </div>
              ))
            }
            </div>
          </div>
          <div className="border-t border-gray-200 py-2 flex-shrink-0">
            <div className="flex" />
            {isOpen ? (
              <div className="px-3 space-y-1">
                {username && (
                  <p className="text-xs text-gray-500 truncate py-1">
                    {username}
                  </p>
                )}
                <a
                  href="/"
                  className="flex items-center h-10 text-gray-600 hover:text-teal-600 font-medium transition text-sm"
                >
                  Página Pública
                </a>
                <button
                  onClick={() => {
                    setIsOpen(false);
                    logout();
                  }}
                  className="flex items-center h-10 w-full text-left text-gray-700 hover:text-red-600 font-medium transition text-sm focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="space-y-1">
                <a
                  href="/"
                  className="flex items-center justify-center h-11 w-full text-gray-500 hover:text-teal-600 transition"
                  title="Página Pública"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                    />
                  </svg>
                </a>
                <button
                  onClick={() => {
                    logout();
                  }}
                  className="flex items-center justify-center h-11 w-full text-gray-500 hover:text-red-600 transition focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                  title="Logout"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

    </>
  );
}
