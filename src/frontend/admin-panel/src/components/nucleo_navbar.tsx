import { Link } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function NucleoSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const { username, logout } = useAuth();

  const navItems = [
    { to: "/nucleo/membros", label: "Membros", short: "Mem" },
    { to: "/nucleo/equipas", label: "Equipas", short: "Equ" },
    { to: "/nucleo/jogos", label: "Jogos", short: "Jog" },
  ];

  return (
    <>
      <aside
        className={`fixed top-0 left-0 h-screen bg-white shadow-xl border-r border-gray-200 z-50 transition-all duration-300 flex flex-col ${isOpen ? 'w-64' : 'w-16'}`}
      >
        <div className="flex items-center justify-between border-b border-gray-200 h-16 flex-shrink-0 px-3">
          {isOpen ? (
            <>
              <Link
                to="/nucleo/dashboard"
                className="text-lg font-bold text-teal-600 hover:text-teal-700 truncate"
              >
                TaçaUA
              </Link>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-red-500 transition ml-2 flex-shrink-0"
                aria-label="Fechar menu"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsOpen(true)}
              className="w-full flex flex-col items-center justify-center gap-1 text-gray-600 hover:text-teal-600 transition"
              aria-label="Abrir menu"
            >
              <span className="block w-5 h-0.5 bg-current"></span>
              <span className="block w-5 h-0.5 bg-current"></span>
              <span className="block w-5 h-0.5 bg-current"></span>
            </button>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto py-2">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              onClick={() => setIsOpen(false)}
              className="flex items-center h-11 px-3 text-gray-700 hover:text-teal-600 hover:bg-teal-50 transition-colors"
              title={!isOpen ? item.label : undefined}
            >
              {isOpen ? (
                <span className="font-medium truncate">{item.label}</span>
              ) : (
                <span className="text-xs font-bold w-full text-center">{item.short}</span>
              )}
            </Link>
          ))}
        </nav>

        <div className="border-t border-gray-200 py-2 flex-shrink-0">
          {isOpen ? (
            <div className="px-3 space-y-1">
              {username && (
                <div className="py-2">
                  <p className="text-sm font-semibold text-gray-800 truncate">{username}</p>
                </div>
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
                className="flex items-center h-10 w-full text-left text-gray-700 hover:text-red-600 font-medium transition text-sm"
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
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </a>
              <button
                onClick={() => {
                  logout();
                }}
                className="flex items-center justify-center h-11 w-full text-gray-500 hover:text-red-600 transition"
                title="Logout"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </aside>

      <div className="w-16 flex-shrink-0" />
    </>
  );
}
