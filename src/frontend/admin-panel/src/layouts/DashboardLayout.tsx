import { useAuth } from '../hooks/useAuth';
import Sidebar from '../components/Sidebar';
import { Navigate, Outlet } from 'react-router-dom';
import { ModalProvider } from '../contexts/ModalContext';
import { useSeason } from '../contexts/SeasonContext';
import { useState } from 'react';


const SeasonSelector = () => {
  // Upper bar component to select the season, shows the currently loaded season and allows changing it like a tab selector
  const { availableSeasons, loadedSeason, selectSeason } = useSeason();
  const [isChangingSeason, setIsChangingSeason] = useState(false);

  const handleSeasonChange = async (seasonId: number) => {
    try {
      setIsChangingSeason(true);
      const selectedSeason = availableSeasons.find(s => s.id === seasonId);
      if (!selectedSeason) throw new Error("Selected season not found");
      await selectSeason(selectedSeason);
    } catch (error) {
      console.error("Failed to change season:", error);
    } finally {
      setIsChangingSeason(false);
    }
  };

  return (
    <div className="flex items-center space-x-4">
      {availableSeasons.map(season => (
        <button
          key={season.id}
          onClick={() => handleSeasonChange(season.id)}
          disabled={isChangingSeason || season.id === loadedSeason?.id}
          className={`px-3 py-1 rounded ${season.id === loadedSeason?.id ? 'bg-teal-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'} transition-colors duration-200`}
        >
          {season.name}
        </button>
      ))}
    </div>
  );
}

/**
 * DashboardLayout wraps all authenticated pages with a sidebar and main content area.
 * Only renders if the user is authenticated.
 */
export default function DashboardLayout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/unauthorized" replace />;
  }

  return (
    <div className="flex min-h-screen">
      <ModalProvider>
        <Sidebar />
        <main className="flex-1 p-6 bg-gray-50">
          <SeasonSelector />
          <Outlet />
        </main>
      </ModalProvider>
    </div>
  );
}
