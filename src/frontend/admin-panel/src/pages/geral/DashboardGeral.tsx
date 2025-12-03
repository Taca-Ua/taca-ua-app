import Sidebar from "../../components/geral_navbar";

function DashboardGeral() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Dashboard - Administrador Geral</h1>
          <p className="text-gray-600 mb-8">Bem-vindo ao painel de administração geral</p>

          {/* Content area */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2 text-teal-600">Torneios </h2>
              <p className="text-3xl font-bold text-gray-800">0</p>
              <p className="text-sm text-gray-500 mt-2">Torneios activos</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2 text-teal-600">Núcleos</h2>
              <p className="text-3xl font-bold text-gray-800">0</p>
              <p className="text-sm text-gray-500 mt-2">Nucleos registrados</p>
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

export default DashboardGeral;
