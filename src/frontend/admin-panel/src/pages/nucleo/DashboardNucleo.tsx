import NucleoSidebar from "../../components/nucleo_navbar";

function DashboardNucleo() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Núcleo</h1>
          <p className="text-gray-600 mb-8">Bem-vindo ao painel de administração do núcleo</p>
          
          {/* Content area */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2 text-teal-600">Membros</h2>
              <p className="text-3xl font-bold text-gray-800">0</p>
              <p className="text-sm text-gray-500 mt-2">Membros registados</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2 text-teal-600">Equipas</h2>
              <p className="text-3xl font-bold text-gray-800">0</p>
              <p className="text-sm text-gray-500 mt-2">Equipas criadas</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2 text-teal-600">Jogos</h2>
              <p className="text-3xl font-bold text-gray-800">0</p>
              <p className="text-sm text-gray-500 mt-2">Jogos agendados</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardNucleo;
