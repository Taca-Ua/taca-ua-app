import { Link } from 'react-router-dom';
import { useState } from 'react';

function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isClassificacaoOpen, setIsClassificacaoOpen] = useState(false);
  const [isParticipantesOpen, setIsParticipantesOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm w-full sticky top-0 z-50">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Navigation Links - Left Side */}
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <Link
              to="/"
              className="flex items-center transition-transform duration-300 ease-in-out hover:scale-105"
            >
              <img src="/logo.png" alt="Taça UA" className="h-10 w-auto" />
            </Link>

            {/* Desktop Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              {/* Classificação Dropdown */}
              <div className="relative group">
                <button
                  onClick={() => setIsClassificacaoOpen(!isClassificacaoOpen)}
                  className="relative text-gray-700 hover:text-teal-600 font-medium transition-all duration-300 ease-in-out flex items-center gap-1 py-2"
                >
                  Classificação
                  <svg
                    className={`w-4 h-4 transition-transform duration-300 ${isClassificacaoOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  <span className="absolute left-0 bottom-0 w-0 h-0.5 bg-teal-600 transition-all duration-300 ease-in-out group-hover:w-full"></span>
                </button>

                {/* Dropdown Menu */}
                {isClassificacaoOpen && (
                  <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg py-2 border border-gray-100 z-50">
                    <Link
                      to="/ranking"
                      className="block px-4 py-2 text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      onClick={() => setIsClassificacaoOpen(false)}
                    >
                      Ranking Geral
                    </Link>
                    <Link
                      to="/ranking/modalidade"
                      className="block px-4 py-2 text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      onClick={() => setIsClassificacaoOpen(false)}
                    >
                      Ranking por Modalidade
                    </Link>
                    <Link
                      to="/torneios"
                      className="block px-4 py-2 text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      onClick={() => setIsClassificacaoOpen(false)}
                    >
                      Torneios
                    </Link>
                  </div>
                )}
              </div>

              {/* Participantes Dropdown */}
              <div className="relative group">
                <button
                  onClick={() => setIsParticipantesOpen(!isParticipantesOpen)}
                  className="relative text-gray-700 hover:text-teal-600 font-medium transition-all duration-300 ease-in-out flex items-center gap-1 py-2"
                >
                  Participantes
                  <svg
                    className={`w-4 h-4 transition-transform duration-300 ${isParticipantesOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  <span className="absolute left-0 bottom-0 w-0 h-0.5 bg-teal-600 transition-all duration-300 ease-in-out group-hover:w-full"></span>
                </button>

                {isParticipantesOpen && (
                  <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg py-2 border border-gray-100 z-50">
                    <Link
                      to="/nucleos"
                      className="block px-4 py-2 text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      onClick={() => setIsParticipantesOpen(false)}
                    >
                      Núcleos
                    </Link>
                    <Link
                      to="/equipas"
                      className="block px-4 py-2 text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      onClick={() => setIsParticipantesOpen(false)}
                    >
                      Equipas
                    </Link>
                    {/* <Link
                      to="/estudantes"
                      className="block px-4 py-2 text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors"
                      onClick={() => setIsParticipantesOpen(false)}
                    >
                      Estudantes
                    </Link> */}
                  </div>
                )}
              </div>

              <Link
                to="/calendario"
                className="relative text-gray-700 hover:text-teal-600 font-medium transition-all duration-300 ease-in-out group"
              >
                Calendário
                <span className="absolute left-0 bottom-0 w-0 h-0.5 bg-teal-600 transition-all duration-300 ease-in-out group-hover:w-full"></span>
              </Link>
              <Link
                to="/regulamentos"
                className="relative text-gray-700 hover:text-teal-600 font-medium transition-all duration-300 ease-in-out group"
              >
                Regulamentos
                <span className="absolute left-0 bottom-0 w-0 h-0.5 bg-teal-600 transition-all duration-300 ease-in-out group-hover:w-full"></span>
              </Link>
            </div>
          </div>

          {/* Admin Button - Desktop Only */}
          <a
            href="/admin/"
            className="hidden md:block bg-teal-500 hover:bg-teal-600 text-white px-4 py-2 rounded-md font-medium transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg"
          >
            Página Admin
          </a>

          {/* Mobile Hamburger Button */}
          <div className="md:hidden relative">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex flex-col items-center justify-center w-10 h-10 text-gray-700 hover:text-teal-600 focus:outline-none transition-all duration-300"
              aria-label="Toggle menu"
              type="button"
            >
              <span className={`block w-6 h-0.5 bg-current transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
              <span className={`block w-6 h-0.5 bg-current mt-1.5 transition-all duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
              <span className={`block w-6 h-0.5 bg-current mt-1.5 transition-all duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
            </button>

            {/* Mobile Dropdown Menu */}
            {isMenuOpen && (
              <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-xl py-3 border border-gray-100 z-50 animate-in fade-in slide-in-from-top-2 duration-300">
                {/* Classificação with submenu */}
                <div className="px-5 py-3">
                  <div className="text-gray-700 font-semibold mb-2 text-base">Classificação</div>
                  <Link
                    to="/ranking"
                    className="block pl-5 py-3 text-base text-gray-600 hover:text-teal-600 transition-colors rounded hover:bg-teal-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Ranking Geral
                  </Link>
                  <Link
                    to="/ranking/modalidade"
                    className="block pl-5 py-3 text-base text-gray-600 hover:text-teal-600 transition-colors rounded hover:bg-teal-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Ranking por Modalidade
                  </Link>
                  <Link
                    to="/torneios"
                    className="block pl-5 py-3 text-base text-gray-600 hover:text-teal-600 transition-colors rounded hover:bg-teal-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Torneios
                  </Link>
                </div>

                {/* Participantes with submenu */}
                <div className="px-5 py-3">
                  <div className="text-gray-700 font-semibold mb-2 text-base">Participantes</div>
                  <Link
                    to="/nucleos"
                    className="block pl-5 py-3 text-base text-gray-600 hover:text-teal-600 transition-colors rounded hover:bg-teal-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Núcleos
                  </Link>
                  <Link
                    to="/equipas"
                    className="block pl-5 py-3 text-base text-gray-600 hover:text-teal-600 transition-colors rounded hover:bg-teal-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Equipas
                  </Link>
                  {/* <Link
                    to="/estudantes"
                    className="block pl-5 py-3 text-base text-gray-600 hover:text-teal-600 transition-colors rounded hover:bg-teal-50"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Estudantes
                  </Link> */}
                </div>

                <Link
                  to="/calendario"
                  className="block px-5 py-3 text-base text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors rounded mx-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Calendário
                </Link>
                <Link
                  to="/regulamentos"
                  className="block px-5 py-3 text-base text-gray-700 hover:bg-teal-50 hover:text-teal-600 transition-colors rounded mx-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Regulamentos
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
