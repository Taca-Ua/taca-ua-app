import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';
import { tournamentsApi, type Tournament, type TournamentCreate } from '../../api/tournaments';
import { modalitiesApi, type Modality } from '../../api/modalities';
import { teamsApi, type Team } from '../../api/teams';

const Torneios = () => {
  const navigate = useNavigate();

  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [modalities, setModalities] = useState<Modality[]>([]);
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false);

  // Campos de criação
  const [name, setName] = useState('');
  const [modalityId, setModalityId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [teams, setTeams] = useState<string[]>([]);
  const [newTeamId, setNewTeamId] = useState('');

  // Filtros
  const [filterStatus, setFilterStatus] = useState('');
  const [filterModality, setFilterModality] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [tournamentsData, modalitiesData, teamsData] = await Promise.all([
        tournamentsApi.getAll(),
        modalitiesApi.getAll(),
        teamsApi.getAll(true), // Get all teams
      ]);
      setTournaments(tournamentsData);
      setModalities(modalitiesData);
      setAllTeams(teamsData);
      setError('');
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTeam = () => {
    if (!newTeamId.trim()) return;

    if (teams.includes(newTeamId)) {
      alert("Essa equipa já foi adicionada.");
      return;
    }

    setTeams([...teams, newTeamId]);
    setNewTeamId('');
    setIsTeamModalOpen(false);
  };

  const handleRemoveTeam = (id: string) => {
    setTeams(teams.filter(t => t !== id));
  };

  const handleCreate = async () => {
    if (!name.trim() || !modalityId) {
      alert("Nome e modalidade são obrigatórios.");
      return;
    }

    try {
      const newTournamentData: TournamentCreate = {
        name,
        modality_id: modalityId,
        start_date: startDate || undefined,
        teams: teams.length > 0 ? teams : undefined,
      };

      const newTournament = await tournamentsApi.create(newTournamentData);
      setTournaments([...tournaments, newTournament]);
      setError('');

      // Reset
      setName('');
      setModalityId('');
      setStartDate('');
      setTeams([]);
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to create tournament:', err);
      setError('Erro ao criar torneio');
    }
  };

  const filtered = tournaments.filter(t =>
    (!filterStatus || t.status === filterStatus) &&
    (!filterModality || t.modality_name === filterModality)
  );

  // Get unique modality names from tournaments
  const availableModalities = useMemo(() => {
    const modalitySet = new Set<string>();
    tournaments.forEach(t => {
      if (t.modality_name) {
        modalitySet.add(t.modality_name);
      }
    });
    return Array.from(modalitySet).sort();
  }, [tournaments]);

  // Get teams filtered by selected modality
  const availableTeams = useMemo(() => {
    if (!modalityId) return [];
    const selectedModality = modalities.find(m => m.id === modalityId);
    if (!selectedModality) return [];
    return allTeams.filter(team => team.modality_name === selectedModality.name);
  }, [modalityId, allTeams, modalities]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Torneios</h1>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-md"
          >
            + Criar Torneio
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {/* Filtros */}
        <div className="flex gap-6 mb-6">
          <div>
            <label className="block mb-1 font-medium text-gray-700">Estado</label>
            <select
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
              className="border px-3 py-2 rounded-md"
            >
              <option value="">Todos</option>
              <option value="draft">Draft</option>
              <option value="active">Ativo</option>
              <option value="finished">Finalizado</option>
            </select>
          </div>

          <div>
            <label className="block mb-1 font-medium text-gray-700">Modalidade</label>
            <select
              value={filterModality}
              onChange={e => setFilterModality(e.target.value)}
              className="border px-3 py-2 rounded-md"
            >
              <option value="">Todas</option>
              {availableModalities.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Lista */}
        <div className="bg-white shadow-md rounded-lg p-6 space-y-3">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : filtered.length > 0 ? (
            filtered.map(t => (
              <div
                key={t.id}
                onClick={() => navigate(`/geral/torneios/${t.id}`)}
                className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer flex justify-between"
              >
                <div className="font-medium">{t.name}</div>
                <div className="text-sm text-teal-600">
                  {t.modality_name} | {t.status}
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center">Nenhum torneio encontrado.</p>
          )}
        </div>
      </div>

      {/* MODAL CRIAR */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg w-full max-w-lg">

            <h2 className="text-2xl font-bold mb-6">Criar Torneio</h2>

            <div className="space-y-4">

              {/* Nome */}
              <div>
                <label className="font-medium">Nome <span className="text-red-500">*</span></label>
                <input
                  className="border w-full px-4 py-2 rounded-md"
                  value={name}
                  onChange={e => setName(e.target.value)}
                />
              </div>

              {/* Modalidade */}
              <div>
                <label className="font-medium">Modalidade <span className="text-red-500">*</span></label>
                <select
                  className="border w-full px-4 py-2 rounded-md bg-white"
                  value={modalityId}
                  onChange={e => {
                    setModalityId(e.target.value);
                    setTeams([]); // Reset teams when modality changes
                  }}
                >
                  <option value="">Selecionar</option>
                  {modalities.map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>

              {/* Data */}
              <div>
                <label className="font-medium">Data de Início</label>
                <input
                  type="date"
                  className="border w-full px-4 py-2 rounded-md"
                  value={startDate}
                  onChange={e => setStartDate(e.target.value)}
                />
              </div>

              {/* EQUIPAS */}
              <div>
                <label className="font-medium">Equipas</label>

                {!modalityId ? (
                  <p className="text-sm text-gray-500 mt-2 italic">Selecione uma modalidade primeiro</p>
                ) : (
                  <>
                    <div className="mt-2 space-y-2 max-h-40 overflow-y-auto">
                      {teams.map(teamId => {
                        const team = allTeams.find(t => t.id === teamId);
                        return (
                          <div key={teamId} className="bg-gray-100 px-4 py-2 rounded-md flex justify-between">
                            <span>{team?.name || `Equipa ${teamId}`}</span>
                            <button
                              onClick={() => handleRemoveTeam(teamId)}
                              className="text-red-500 hover:text-red-700"
                            >
                              Remover
                            </button>
                          </div>
                        );
                      })}

                      {teams.length === 0 && (
                        <p className="text-gray-500 italic">Nenhuma equipa adicionada.</p>
                      )}
                    </div>

                    <button
                      onClick={() => setIsTeamModalOpen(true)}
                      disabled={availableTeams.length === 0}
                      className="mt-3 bg-teal-500 text-white px-4 py-2 rounded-md disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      + Adicionar Equipa
                    </button>
                    {availableTeams.length === 0 && (
                      <p className="text-sm text-gray-500 mt-1">Nenhuma equipa disponível para esta modalidade</p>
                    )}
                  </>
                )}
              </div>

            </div>

            {/* Botões */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsModalOpen(false)}
                className="flex-1 bg-gray-300 py-2 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreate}
                className="flex-1 bg-teal-500 text-white py-2 rounded-md"
              >
                Criar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MODAL ADICIONAR EQUIPA */}
      {isTeamModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Adicionar Equipa</h2>

            <label className="font-medium">Selecionar Equipa</label>
            <select
              value={newTeamId}
              onChange={e => setNewTeamId(e.target.value)}
              className="border w-full px-4 py-2 rounded-md mt-1 bg-white"
            >
              <option value="">Selecionar equipa...</option>
              {availableTeams
                .filter(team => !teams.includes(team.id))
                .map(team => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.course_name})
                  </option>
                ))}
            </select>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => {
                  setIsTeamModalOpen(false);
                  setNewTeamId('');
                }}
                className="flex-1 bg-gray-300 py-2 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddTeam}
                disabled={!newTeamId}
                className="flex-1 bg-teal-500 text-white py-2 rounded-md disabled:bg-gray-300 disabled:cursor-not-allowed"
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

export default Torneios;
