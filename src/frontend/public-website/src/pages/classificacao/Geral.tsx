import { useState } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';

function ClassificacaoGeral() {
  const [selectedEpoca, setSelectedEpoca] = useState('25/26');

  // Mock data - replace with API call later
  const allRankings = {
    '25/26': [
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
    ],
    '24/25': [
      { position: 1, name: 'NEMAT', points: 450 },
      { position: 2, name: 'NEI', points: 420 },
      { position: 3, name: 'NET', points: 380 },
      { position: 4, name: 'NEM', points: 350 },
      { position: 5, name: 'NEEC', points: 320 },
      { position: 6, name: 'NEGeo', points: 290 },
      { position: 7, name: 'NEGPT', points: 260 },
      { position: 8, name: 'NED', points: 240 },
      { position: 9, name: 'NEEA', points: 220 },
      { position: 10, name: 'NEECT', points: 200 },
    ],
    '23/24': [
      { position: 1, name: 'NET', points: 520 },
      { position: 2, name: 'NEI', points: 490 },
      { position: 3, name: 'NEM', points: 460 },
      { position: 4, name: 'NEMAT', points: 430 },
      { position: 5, name: 'NEEC', points: 400 },
      { position: 6, name: 'NEGeo', points: 370 },
      { position: 7, name: 'NEGPT', points: 340 },
      { position: 8, name: 'NED', points: 310 },
      { position: 9, name: 'NEEA', points: 280 },
      { position: 10, name: 'NEECT', points: 250 },
    ],
  };

  const rankings = allRankings[selectedEpoca as keyof typeof allRankings] || [];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">
            Classificação Geral
          </h1>

          {/* Época Filter */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Época
            </label>
            <select
              value={selectedEpoca}
              onChange={(e) => setSelectedEpoca(e.target.value)}
              className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
            >
              <option value="25/26">25/26</option>
              <option value="24/25">24/25</option>
              <option value="23/24">23/24</option>
            </select>
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

export default ClassificacaoGeral;
