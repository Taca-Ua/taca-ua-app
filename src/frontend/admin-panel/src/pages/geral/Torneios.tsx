import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

// ===== MOCK DATA =====
const mockModalities = [
  { id: 1, name: "Futebol" },
  { id: 2, name: "Basquete" },
  { id: 3, name: "Andebol" },
];

const years = ['25/26', '24/25', '23/24', '22/23'];

interface Torneio {
  id: number;
  name: string;
  modality_id: number;
  year: string;
  rules?: string;
  teams?: number[];
  start_date?: string;
  status: 'draft' | 'active' | 'finished';
}

const mockTournaments: Torneio[] = [
  { id: 1, name: "Torneio Futebol A", modality_id: 1, year: "25/26", teams: [1, 2, 3, 4], status: "active" },
  { id: 2, name: "Torneio Basquete Elite", modality_id: 2, year: "25/26", teams: [5, 6], status: "draft" },
  { id: 3, name: "Torneio Futsal Pro", modality_id: 4, year: "24/25", teams: [7, 8, 9], status: "finished" },
];

const Torneios = () => {
  const navigate = useNavigate();

  const [tournaments, setTournaments] = useState<Torneio[]>(mockTournaments);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false);

  // Campos de criação
  const [name, setName] = useState('');
  const [modalityId, setModalityId] = useState('');
  const [year, setYear] = useState('');
  const [rules, setRules] = useState('');
  const [startDate, setStartDate] = useState('');
  const [teams, setTeams] = useState<number[]>([]);
  const [newTeamId, setNewTeamId] = useState('');

  // Filtros
  const [filterStatus, setFilterStatus] = useState('');
  const [filterModality, setFilterModality] = useState('');

  const handleAddTeam = () => {
    if (!newTeamId.trim()) return;

    const id = Number(newTeamId);

    if (teams.includes(id)) {
      alert("Essa equipa já foi adicionada.");
      return;
    }

    setTeams([...teams, id]);
    setNewTeamId('');
    setIsTeamModalOpen(false);
  };

  const handleRemoveTeam = (id: number) => {
    setTeams(teams.filter(t => t !== id));
  };

  const handleCreate = () => {
    if (!name.trim() || !modalityId || !year) {
      alert("Nome, modalidade e época são obrigatórios.");
      return;
    }

    const newTournament: Torneio = {
      id: tournaments.length + 1,
      name,
      modality_id: Number(modalityId),
      year: year,
      rules: rules || undefined,
      start_date: startDate || undefined,
      teams: teams.length > 0 ? teams : undefined,
      status: "draft",
    };

    setTournaments([...tournaments, newTournament]);

    // Reset
    setName('');
    setModalityId('');
    setYear('');
    setRules('');
    setStartDate('');
    setTeams([]);
    setIsModalOpen(false);
  };

  const filtered = tournaments.filter(t =>
    (!filterStatus || t.status === filterStatus) &&
    (!filterModality || String(t.modality_id) === filterModality)
  );

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
            <label className="block mb-1 font-medium text-gray-700">Modalidade ID</label>
            <input
              type="number"
              value={filterModality}
              onChange={e => setFilterModality(e.target.value)}
              placeholder="ex: 1"
              className="border px-3 py-2 rounded-md"
            />
          </div>

        </div>

        {/* Lista */}
        <div className="bg-white shadow-md rounded-lg p-6 space-y-3">
          {filtered.length > 0 ? filtered.map(t => (
            <div
              key={t.id}
              onClick={() => navigate(`/geral/torneios/${t.id}`)}
              className="px-6 py-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer flex justify-between"
            >
              <div className="font-medium">{t.name}</div>
              <div className="text-sm text-teal-600">
                Modalidade {t.modality_id} | época {t.year} | {t.status}
              </div>
            </div>
          )) : (
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
                  onChange={e => setModalityId(e.target.value)}
                >
                  <option value="">Selecionar</option>
                  {mockModalities.map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>

              {/* Season */}
              <div>
                <label className="font-medium">Época <span className="text-red-500">*</span></label>
                <select
                  className="border w-full px-4 py-2 rounded-md bg-white"
                  value={year}
                  onChange={e => setYear(e.target.value)}
                >
                  <option value="">Selecionar</option>
                  {years.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* Rules */}
              <div>
                <label className="font-medium">Regras (JSON)</label>
                <textarea
                  className="border w-full px-4 py-2 rounded-md min-h-[80px]"
                  value={rules}
                  onChange={e => setRules(e.target.value)}
                />
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

                <div className="mt-2 space-y-2 max-h-40 overflow-y-auto">
                  {teams.map(team => (
                    <div key={team} className="bg-gray-100 px-4 py-2 rounded-md flex justify-between">
                      <span>Equipa {team}</span>
                      <button
                        onClick={() => handleRemoveTeam(team)}
                        className="text-red-500"
                      >
                        Remover
                      </button>
                    </div>
                  ))}

                  {teams.length === 0 && (
                    <p className="text-gray-500 italic">Nenhuma equipa adicionada.</p>
                  )}
                </div>

                <button
                  onClick={() => setIsTeamModalOpen(true)}
                  className="mt-3 bg-teal-500 text-white px-4 py-2 rounded-md"
                >
                  + Adicionar Equipa
                </button>
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
        <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Adicionar Equipa</h2>

            <label>ID da Equipa</label>
            <input
              type="number"
              value={newTeamId}
              onChange={e => setNewTeamId(e.target.value)}
              className="border w-full px-4 py-2 rounded-md mt-1"
            />

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsTeamModalOpen(false)}
                className="flex-1 bg-gray-300 py-2 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddTeam}
                className="flex-1 bg-teal-500 text-white py-2 rounded-md"
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
