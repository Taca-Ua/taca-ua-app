import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';

interface Match {
  id: number;
  team1: string;
  team2: string;
  date: string;
  time: string;
  location: string;
  modality: string;
}

const Jogos = () => {
  const navigate = useNavigate();

  // Mock data for matches (Replace with API call)
  const [matches] = useState<Match[]>([
    {
      id: 1,
      team1: 'Equipa 1',
      team2: 'Equipa 4',
      date: '2025-12-05',
      time: '14:00',
      location: 'Campo Principal',
      modality: 'Futebol',
    },
    {
      id: 2,
      team1: 'Equipa 2',
      team2: 'Equipa 8',
      date: '2025-12-03',
      time: '16:00',
      location: 'Pavilhão A',
      modality: 'Basquetebol',
    },
    {
      id: 3,
      team1: 'Equipa 3',
      team2: 'Equipa 9',
      date: '2025-11-28',
      time: '18:00',
      location: 'Pavilhão B',
      modality: 'Voleibol',
    },
    {
      id: 4,
      team1: 'Equipa 5',
      team2: 'Equipa 4',
      date: '2025-12-10',
      time: '15:30',
      location: 'Pavilhão C',
      modality: 'Futsal',
    },
    {
      id: 5,
      team1: 'Equipa 6',
      team2: 'Equipa 7',
      date: '2025-11-25',
      time: '17:00',
      location: 'Campo Secundário',
      modality: 'Andebol',
    },
    {
      id: 6,
      team1: 'Equipa 1',
      team2: 'Equipa 2',
      date: '2025-12-15',
      time: '19:00',
      location: 'Estádio Central',
      modality: 'Rugby',
    },
    {
      id: 7,
      team1: 'Equipa 7',
      team2: 'Equipa 8',
      date: '2025-12-12',
      time: '16:30',
      location: 'Pavilhão B',
      modality: 'Basquetebol',
    },
    {
      id: 8,
      team1: 'Equipa 3',
      team2: 'Equipa 6',
      date: '2025-12-08',
      time: '18:30',
      location: 'Campo Secundário',
      modality: 'Futebol',
    },
    {
      id: 9,
      team1: 'Equipa 5',
      team2: 'Equipa 9',
      date: '2025-12-20',
      time: '20:00',
      location: 'Pavilhão A',
      modality: 'Voleibol',
    },
  ]);

  const [filterModality, setFilterModality] = useState<string>('');
  const [filterTeam, setFilterTeam] = useState<string>('');

  const modalities = [
    'Futebol',
    'Futsal',
    'Basquetebol',
    'Voleibol',
    'Andebol',
    'Rugby',
  ];

  const teams = [
    'Equipa 1',
    'Equipa 2',
    'Equipa 3',
    'Equipa 4',
    'Equipa 5',
    'Equipa 6',
    'Equipa 7',
    'Equipa 8',
    'Equipa 9',
  ];

  // Filter matches by modality and team
  let filteredMatches = matches;
  
  if (filterModality) {
    filteredMatches = filteredMatches.filter((match) => match.modality === filterModality);
  }
  
  if (filterTeam) {
    filteredMatches = filteredMatches.filter(
      (match) => match.team1 === filterTeam || match.team2 === filterTeam
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />
      
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Jogos</h1>
          </div>

          {/* Filters */}
          <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="modalityFilter" className="block text-gray-700 font-medium mb-2">
                Modalidade
              </label>
              <select
                id="modalityFilter"
                value={filterModality}
                onChange={(e) => setFilterModality(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="">Selecionar Modalidade</option>
                {modalities.map((modality) => (
                  <option key={modality} value={modality}>
                    {modality}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="teamFilter" className="block text-gray-700 font-medium mb-2">
                Equipa
              </label>
              <select
                id="teamFilter"
                value={filterTeam}
                onChange={(e) => setFilterTeam(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              >
                <option value="">Selecionar Equipa</option>
                {teams.map((team) => (
                  <option key={team} value={team}>
                    {team}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Matches List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Jogos</h2>
            <div className="space-y-3">
              {filteredMatches.length > 0 ? (
                filteredMatches.map((match) => (
                  <div
                    key={match.id}
                    onClick={() => navigate(`/nucleo/jogos/${match.id}`)}
                    className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-gray-800 font-bold text-lg">
                        {match.team1} vs {match.team2}
                      </span>
                      <span className="text-teal-600 text-sm font-medium">{match.modality}</span>
                    </div>
                    <div className="flex gap-6 text-sm text-gray-600">
                      <span>
                        <span className="font-medium">Data:</span> {new Date(match.date).toLocaleDateString('pt-PT')}
                      </span>
                      <span>
                        <span className="font-medium">Hora:</span> {match.time}
                      </span>
                      <span>
                        <span className="font-medium">Local:</span> {match.location}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">
                  Nenhum jogo encontrado.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Jogos;
