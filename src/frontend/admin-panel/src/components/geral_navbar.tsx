import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="bg-white shadow-sm w-full sticky top-0 z-50">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">

          {/* Button to open*/}
          {!isOpen && (
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="flex flex-col top-4 left-4 items-center justify-center w-10 h-10 text-gray-700 hover:text-teal-600 focus:outline-none transition-all duration-300"
              aria-label="Toggle menu"
              type="button"
            >
              <span className="block w-6 h-0.5 bg-current"></span>
              <span className="block w-6 h-0.5 bg-current mt-1.5"></span>
              <span className="block w-6 h-0.5 bg-current mt-1.5"></span>
            </button>
          )}

          {/* OVERLAY OSCURO */}
          {isOpen && (
            <div
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 animate-in fade-in"
            ></div>
          )}

          {/* SIDEBAR */}
          <aside
            className={`fixed top-0 left-0 h-full w-72 bg-white shadow-xl border-r border-gray-200 z-50
                        transform transition-transform duration-300
                        ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
          >
            <div className="p-6 h-full flex flex-col">
              {/* HEADER */}
              <div className="flex items-center justify-between mb-8">
                <Link
                  to="/geral/dashboard"
                  className="text-xl font-bold text-teal-600 transition-all duration-300 ease-in-out hover:text-teal-700 group"
                >
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6">T</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 delay-75">a</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6 delay-100">ç</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 delay-150">a</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6 delay-200">U</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 delay-300">a</span>
                </Link>

                {/* BOTÓN DE CERRAR */}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-600 hover:text-red-500 transition bg-white"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* NAV */}
              <nav className="space-y-5 flex-1">

              {/* Links*/}
              <Link
                to="/geral/administradores"
                className="block text-gray-700 hover:text-teal-600 font-medium transition"
                onClick={() => setIsOpen(false)}
              >
                Administradores
              </Link>

              <Link
                to="/geral/modalidades"
                className="block text-gray-700 hover:text-teal-600 font-medium transition"
                onClick={() => setIsOpen(false)}
              >
                Modalidades
              </Link>

              <Link
                to="/geral/nucleos"
                className="block text-gray-700 hover:text-teal-600 font-medium transition"
                onClick={() => setIsOpen(false)}
              >
                Núcleo
              </Link>

              <Link
                to="/geral/torneios"
                className="block text-gray-700 hover:text-teal-600 font-medium transition"
                onClick={() => setIsOpen(false)}
              >
                Torneios
              </Link>

              <Link
                to="/geral/regulamentos"
                className="block text-gray-700 hover:text-teal-600 font-medium transition"
                onClick={() => setIsOpen(false)}
              >
                Regulamentos
              </Link>

              <Link
                to="/socios"
                className="block text-gray-700 hover:text-teal-600 font-medium transition"
                onClick={() => setIsOpen(false)}
              >
                Sócios
              </Link>

              {/* 📌 Final seccion */}
              <div className="mt-auto pt-6 pb-6 border-t border-gray-200 space-y-4">

                <a
                  href="/"
                  className="block text-gray-600 hover:text-teal-600 font-medium transition"
                >
                  Página Pública
                </a>

                <button
                  onClick={() => {
                    setIsOpen(false);
                    logout();
                    navigate('/login/geral');
                  }}
                  className="block text-left w-full hover:text-red-600 font-medium transition"
                >
                  Logout {user?.full_name && `(${user.full_name})`}
                </button>

              </div>

            </nav>
            </div>
          </aside>
        </div>
      </div>
    </nav>
  );
}
