import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
// Import the Keycloak hook, replacing the previous generic useAuth hook
import { useKeycloak } from "../auth/KeycloakProvider";

export default function NucleoSidebar() {
  const [isOpen, setIsOpen] = useState(false);

  // Use useKeycloak to get the logout function and access the Keycloak object
  const { logout, keycloak } = useKeycloak();

  const navigate = useNavigate();

  // Extract user information directly from the Keycloak token payload (tokenParsed)
  const userName = keycloak.tokenParsed?.name || keycloak.tokenParsed?.preferred_username;
  // Note: 'course_abbreviation' and 'full_name' must be mapped as claims in Keycloak
  // or derived from existing claims (e.g., in a custom Keycloak mapper)
  const userFullName = keycloak.tokenParsed?.full_name;
  const userCourseAbbreviation = keycloak.tokenParsed?.course_abbreviation;


  return (
    <nav className="bg-white shadow-sm w-full sticky top-0 z-50">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">

          {/* Button to open the sidebar */}
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

          {/* DARK OVERLAY */}
          {isOpen && (
            <div
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 animate-in fade-in"
            ></div>
          )}

          {/* SIDEBAR CONTAINER */}
          <aside
            className={`fixed top-0 left-0 h-full w-72 bg-white shadow-xl border-r border-gray-200 z-50
                        transform transition-transform duration-300
                        ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
          >
            <div className="p-6 h-full flex flex-col">
              {/* HEADER (Logo/Title and Close Button) */}
              <div className="flex items-center justify-between mb-8">
                <Link
                  to="/nucleo/dashboard"
                  className="text-xl font-bold text-teal-600 transition-all duration-300 ease-in-out hover:text-teal-700 group"
                >
                  {/* TacaUa Animated Title */}
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6">T</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 delay-75">a</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6 delay-100">ç</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 delay-150">a</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6 delay-200">U</span>
                  <span className="inline-block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 delay-300">a</span>
                </Link>

                {/* CLOSE BUTTON */}
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

              {/* NAVIGATION LINKS */}
              <nav className="space-y-5 flex-1">

                {/* Links for Nucleo Admin */}
                <Link
                  to="/nucleo/membros"
                  className="block text-gray-700 hover:text-teal-600 font-medium transition"
                  onClick={() => setIsOpen(false)}
                >
                  Membros
                </Link>

                <Link
                  to="/nucleo/equipas"
                  className="block text-gray-700 hover:text-teal-600 font-medium transition"
                  onClick={() => setIsOpen(false)}
                >
                  Equipas
                </Link>

                <Link
                  to="/nucleo/jogos"
                  className="block text-gray-700 hover:text-teal-600 font-medium transition"
                  onClick={() => setIsOpen(false)}
                >
                  Jogos
                </Link>

                {/* Final Section */}
                <div className="mt-auto pt-6 pb-6 border-t border-gray-200 space-y-4">
                  {/* User Profile Display (Uses Keycloak claims) */}
                  {userName && (
                    <div className="mb-4 p-3 bg-teal-50 rounded-lg">
                      <p className="text-sm font-semibold text-teal-800">{userFullName || userName}</p>
                      <p className="text-xs text-teal-600">{userCourseAbbreviation || "Nucleo Admin"}</p>
                    </div>
                  )}

                  <a
                    href="/"
                    className="block text-gray-600 hover:text-teal-600 font-medium transition"
                  >
                    Página Pública
                  </a>

                  {/* LOGOUT BUTTON */}
                  <button
                    onClick={() => {
                      // Call Keycloak's logout function
                      logout();
                      setIsOpen(false);
                      // Keycloak handles the final redirect, so manual navigate
                      // to '/login/nucleo' is usually unnecessary and redundant.
                    }}
                    className="block text-left w-full text-gray-700 hover:text-red-600 font-medium transition"
                  >
                    Logout
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
