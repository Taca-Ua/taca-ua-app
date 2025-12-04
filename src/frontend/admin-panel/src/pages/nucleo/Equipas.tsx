import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NucleoSidebar from '../../components/nucleo_navbar';
import { teamsApi } from '../../api/teams';
import type { Team } from '../../api/teams';
import { modalitiesApi } from '../../api/modalities';
import type { Modality } from '../../api/modalities';

const Equipas = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTeamName, setNewTeamName] = useState('');
  const [selectedModality, setSelectedModality] = useState('');
  const [newTeamDescription, setNewTeamDescription] = useState('');
  const [teams, setTeams] = useState<Team[]>([]);
  const [allModalities, setAllModalities] = useState<Modality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterModality, setFilterModality] = useState('');

  // Get only modalities that have teams (for filtering)
  const availableModalities = allModalities.filter(modality =>
    teams.some(team => team.modality_id === modality.id)
  );

  // Fetch teams and modalities from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch both teams and modalities in parallel
        const [fetchedTeams, fetchedModalities] = await Promise.all([
          teamsApi.getAll(),
          modalitiesApi.getAll(),
        ]);

        console.log('Fetched teams:', fetchedTeams);
        console.log('Fetched modalities:', fetchedModalities);

        setTeams(fetchedTeams);
        setAllModalities(fetchedModalities);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Erro ao carregar dados. Por favor, tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddTeam = async () => {
    if (!newTeamName.trim()) {
      alert('Por favor, preencha o nome da equipa.');
      return;
    }

    if (!selectedModality) {
      alert('Por favor, selecione uma modalidade.');
      return;
    }

    try {
      const newTeam = await teamsApi.create({
        modality_id: parseInt(selectedModality),
        name: newTeamName,
        players: [],
      });

      // Add to local state
      setTeams([...teams, newTeam]);
      setNewTeamName('');
      setSelectedModality('');
      setNewTeamDescription('');
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create team:', err);
      alert('Erro ao criar equipa. Por favor, tente novamente.');
    }
  };

  // Helper function to get modality name from ID
  const getModalityName = (modalityId: number) => {
    const modality = allModalities.find(m => m.id === modalityId);
    return modality ? modality.name : `Modalidade ${modalityId}`;
  };

  // Filter teams by modality
  const filteredTeams = filterModality
    ? teams.filter((team) => team.modality_id === parseInt(filterModality))
    : teams;

  return (
    <div className="min-h-screen bg-gray-50">
      <NucleoSidebar />

      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Equipas</h1>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors flex items-center gap-2"
            >
              <span>+</span>
              Adicionar Equipa
            </button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}

          {/* Content - Only show when not loading */}
          {!loading && !error && (
            <>
              {/* Modality Filter */}
              <div className="mb-6">
                <label htmlFor="modalityFilter" className="block text-gray-700 font-medium mb-2">
                  Modalidade
                </label>
                <select
                  id="modalityFilter"
                  value={filterModality}
                  onChange={(e) => setFilterModality(e.target.value)}
                  className="w-64 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Todas as Modalidades</option>
                  {availableModalities.map((modality) => (
                    <option key={modality.id} value={modality.id}>
                      {modality.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Teams List */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Equipas</h2>
                <div className="space-y-3">
                  {filteredTeams.length > 0 ? (
                    filteredTeams.map((team) => (
                      <div
                        key={team.id}
                        onClick={() => navigate(`/nucleo/equipas/${team.id}`)}
                        className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer transition-colors flex justify-between items-center"
                      >
                        <span className="text-gray-800 font-medium">{team.name}</span>
                        <span className="text-teal-600 text-sm font-medium">{getModalityName(team.modality_id)}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-center py-8">
                      Nenhuma equipa encontrada para esta modalidade.
                    </p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Add Team Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 animate-slideUp">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Equipa</h2>

            <div className="space-y-4">
              {/* Team Name */}
              <div>
                <label htmlFor="teamName" className="block text-gray-700 font-medium mb-2">
                  Nome da Equipa <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="teamName"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Digite o nome da equipa"
                />
              </div>

              {/* Modality Selection */}
              <div>
                <label htmlFor="modality" className="block text-gray-700 font-medium mb-2">
                  Modalidade <span className="text-red-500">*</span>
                </label>
                <select
                  id="modality"
                  value={selectedModality}
                  onChange={(e) => setSelectedModality(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Selecionar Modalidade</option>
                  {allModalities.map((modality) => (
                    <option key={modality.id} value={modality.id}>
                      {modality.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-gray-700 font-medium mb-2">
                  Descrição
                </label>
                <textarea
                  id="description"
                  value={newTeamDescription}
                  onChange={(e) => setNewTeamDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 min-h-[100px]"
                  placeholder="Digite a descrição da equipa"
                />
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setNewTeamName('');
                  setSelectedModality('');
                  setNewTeamDescription('');
                }}
                className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-md font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddTeam}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-md font-medium transition-colors"
              >
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Equipas;
