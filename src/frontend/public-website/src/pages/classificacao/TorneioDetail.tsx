import { useParams } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';

function TorneioDet() {
  const { id } = useParams();

  // Mock data - replace with API call later
  const allTournaments = [
    // Época 25/26
    { id: '1', name: 'Torneio 1', modality: 'Futsal Masculino A', epoca: '25/26' },
    { id: '14', name: 'Torneio 14', modality: 'Futsal Masculino A', epoca: '25/26' },
    { id: '25', name: 'Torneio 25', modality: 'Futsal Masculino A', epoca: '25/26' },
    { id: '85', name: 'Torneio 85', modality: 'Futsal Masculino A', epoca: '25/26' },
    { id: '2', name: 'Torneio 2', modality: 'Futsal Feminino', epoca: '25/26' },
    { id: '3', name: 'Torneio 3', modality: 'Futsal Feminino', epoca: '25/26' },
    { id: '4', name: 'Torneio 4', modality: 'Basquetebol', epoca: '25/26' },
    { id: '5', name: 'Torneio 5', modality: 'Basquetebol', epoca: '25/26' },
    { id: '6', name: 'Torneio 6', modality: 'Voleibol', epoca: '25/26' },
    { id: '7', name: 'Torneio 7', modality: 'Voleibol', epoca: '25/26' },
    
    // Época 24/25
    { id: '101', name: 'Torneio 101', modality: 'Futsal Masculino A', epoca: '24/25' },
    { id: '102', name: 'Torneio 102', modality: 'Futsal Masculino A', epoca: '24/25' },
    { id: '103', name: 'Torneio 103', modality: 'Futsal Feminino', epoca: '24/25' },
    { id: '104', name: 'Torneio 104', modality: 'Basquetebol', epoca: '24/25' },
    { id: '105', name: 'Torneio 105', modality: 'Voleibol', epoca: '24/25' },
    
    // Época 23/24
    { id: '201', name: 'Torneio 201', modality: 'Futsal Masculino A', epoca: '23/24' },
    { id: '202', name: 'Torneio 202', modality: 'Futsal Feminino', epoca: '23/24' },
    { id: '203', name: 'Torneio 203', modality: 'Basquetebol', epoca: '23/24' },
    { id: '204', name: 'Torneio 204', modality: 'Voleibol', epoca: '23/24' },
  ];

  // Find the specific tournament by ID
  const tournament = allTournaments.find((t) => t.id === id) || {
    id: id,
    name: `Torneio ${id}`,
    modality: 'Desconhecido',
    epoca: 'N/A',
  };

  const rankings = [
    { position: 1, name: 'NEI', points: 1000000000 },
    { position: 2, name: 'NEM', points: 35 },
    { position: 3, name: 'NET', points: 34 },
    { position: 4, name: 'NEMAT', points: 33 },
    { position: 5, name: 'NEGeo', points: 32 },
    { position: 6, name: 'NEGPT', points: 31 },
    { position: 7, name: 'NEEC', points: 30 },
    { position: 8, name: 'NED', points: 30 },
    { position: 9, name: 'NEEA', points: 30 },
    { position: 10, name: 'NEECT', points: 30 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800">
              {tournament.name}
            </h1>
            <div className="flex items-center gap-3 mt-2">
              <p className="text-xl text-teal-600">{tournament.modality}</p>
              <span className="text-gray-400">•</span>
              <p className="text-xl text-gray-600">Época {tournament.epoca}</p>
            </div>
          </div>

          {/* Rankings Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Posição
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                      Nome
                    </th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">
                      Pontos
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {rankings.map((team, index) => (
                    <tr
                      key={team.position}
                      className={`hover:bg-gray-50 transition-colors ${
                        index === 0 ? 'bg-yellow-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                            index === 0
                              ? 'bg-yellow-400 text-yellow-900'
                              : 'bg-gray-200 text-gray-700'
                          }`}
                        >
                          {team.position}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-lg font-medium text-gray-900">
                        {team.name}
                      </td>
                      <td className="px-6 py-4 text-right text-lg text-gray-700">
                        {team.points.toLocaleString()} pts
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default TorneioDet;
