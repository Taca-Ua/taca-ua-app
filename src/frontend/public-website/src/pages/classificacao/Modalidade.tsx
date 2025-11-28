import { useState } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import TournamentCard from '../../components/TournamentCard';

function ClassificacaoModalidade() {
  const [selectedEpoca, setSelectedEpoca] = useState('25/26');
  const [selectedModalidade, setSelectedModalidade] = useState('Futsal Masculino A');

  // Mock data - replace with API call later
  const allTournaments = [
    // Época 25/26
    { id: '1', name: 'Torneio 1', modality: 'Futsal Masculino A', epoca: '25/26', icon: '⚽' },
    { id: '14', name: 'Torneio 14', modality: 'Futsal Masculino A', epoca: '25/26', icon: '⚽' },
    { id: '25', name: 'Torneio 25', modality: 'Futsal Masculino A', epoca: '25/26', icon: '⚽' },
    { id: '85', name: 'Torneio 85', modality: 'Futsal Masculino A', epoca: '25/26', icon: '⚽' },
    { id: '2', name: 'Torneio 2', modality: 'Futsal Feminino', epoca: '25/26', icon: '⚽' },
    { id: '3', name: 'Torneio 3', modality: 'Futsal Feminino', epoca: '25/26', icon: '⚽' },
    { id: '4', name: 'Torneio 4', modality: 'Basquetebol', epoca: '25/26', icon: '🏀' },
    { id: '5', name: 'Torneio 5', modality: 'Basquetebol', epoca: '25/26', icon: '🏀' },
    { id: '6', name: 'Torneio 6', modality: 'Voleibol', epoca: '25/26', icon: '🏐' },
    { id: '7', name: 'Torneio 7', modality: 'Voleibol', epoca: '25/26', icon: '🏐' },
    
    // Época 24/25
    { id: '101', name: 'Torneio 101', modality: 'Futsal Masculino A', epoca: '24/25', icon: '⚽' },
    { id: '102', name: 'Torneio 102', modality: 'Futsal Masculino A', epoca: '24/25', icon: '⚽' },
    { id: '103', name: 'Torneio 103', modality: 'Futsal Feminino', epoca: '24/25', icon: '⚽' },
    { id: '104', name: 'Torneio 104', modality: 'Basquetebol', epoca: '24/25', icon: '🏀' },
    { id: '105', name: 'Torneio 105', modality: 'Voleibol', epoca: '24/25', icon: '🏐' },
    
    // Época 23/24
    { id: '201', name: 'Torneio 201', modality: 'Futsal Masculino A', epoca: '23/24', icon: '⚽' },
    { id: '202', name: 'Torneio 202', modality: 'Futsal Feminino', epoca: '23/24', icon: '⚽' },
    { id: '203', name: 'Torneio 203', modality: 'Basquetebol', epoca: '23/24', icon: '🏀' },
    { id: '204', name: 'Torneio 204', modality: 'Voleibol', epoca: '23/24', icon: '🏐' },
  ];

  // Filter tournaments based on selected epoca and modality
  const filteredTournaments = allTournaments.filter(
    (tournament) =>
      tournament.epoca === selectedEpoca &&
      tournament.modality === selectedModalidade
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-grow py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 text-gray-800">
            Classificação por Modalidade
          </h1>

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Época
              </label>
              <select
                value={selectedEpoca}
                onChange={(e) => setSelectedEpoca(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
              >
                <option value="25/26">25/26</option>
                <option value="24/25">24/25</option>
                <option value="23/24">23/24</option>
              </select>
            </div>

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Modalidade
              </label>
              <select
                value={selectedModalidade}
                onChange={(e) => setSelectedModalidade(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 bg-white"
              >
                <option value="Futsal Masculino A">Futsal Masculino A</option>
                <option value="Futsal Feminino">Futsal Feminino</option>
                <option value="Basquetebol">Basquetebol</option>
                <option value="Voleibol">Voleibol</option>
              </select>
            </div>
          </div>

          {/* Tournament Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredTournaments.length > 0 ? (
              filteredTournaments.map((tournament) => (
                <TournamentCard
                  key={tournament.id}
                  id={tournament.id}
                  name={tournament.name}
                  modality={tournament.modality}
                  epoca={tournament.epoca}
                  icon={tournament.icon}
                />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-xl text-gray-500">
                  Nenhum torneio encontrado para esta combinação de época e modalidade.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default ClassificacaoModalidade;
