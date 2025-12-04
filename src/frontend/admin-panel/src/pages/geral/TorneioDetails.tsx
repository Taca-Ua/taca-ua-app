import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/geral_navbar';

interface Torneio {
  id: number;
  name: string;
  modality_id: number;
  year: string;
  rules?: string;
  teams: number[];
  start_date?: string;
  status: 'draft' | 'active' | 'finished';
}

// MOCK MANTENIDO
const mockTournaments: Torneio[] = [
  { id: 1, name: "Torneio Futebol A", modality_id: 1, year: "25/26", teams: [1, 2, 3, 4], status: "active" },
  { id: 2, name: "Torneio Basquete Elite", modality_id: 2, year: "25/26", teams: [5, 6], status: "draft" },
  { id: 3, name: "Torneio Futsal Pro", modality_id: 4, year: "24/25", teams: [7, 8, 9], status: "finished" },
];

const TorneioDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const initial = useMemo(
    () => mockTournaments.find(t => t.id === Number(id)) || null,
    [id]
  );

  const [tournament, setTournament] = useState(initial);

  const [isEditModal, setIsEditModal] = useState(false);
  const [isAddTeamModal, setIsAddTeamModal] = useState(false);

  // Campos edición
  const [editName, setEditName] = useState('');
  const [editRules, setEditRules] = useState('');
  const [editStartDate, setEditStartDate] = useState('');

  // Novo team
  const [newTeamId, setNewTeamId] = useState('');

  if (!tournament) {
    return <div className="p-10 text-center text-red-600">Torneio não encontrado.</div>;
  }

  const openEdit = () => {
    setEditName(tournament.name);
    setEditRules(tournament.rules ?? '');
    setEditStartDate(tournament.start_date ?? '');
    setIsEditModal(true);
  };

  const saveEdit = () => {
    setTournament({
      ...tournament,
      name: editName,
      rules: editRules || undefined,
      start_date: editStartDate || undefined,
    });
    setIsEditModal(false);
  };

  // DELETE /api/admin/tournaments/{id}
  const deleteTournament = () => {
    if (!window.confirm("Tem certeza que deseja eliminar este torneio?")) return;
    navigate('/geral/torneios');
  };

  // POST /api/admin/tournaments/{id}/finish
  const finishTournament = () => {
    if (!window.confirm("Finalizar torneio? Isso bloqueará edições.")) return;

    setTournament({ ...tournament, status: 'finished' });
  };

  const addTeam = () => {
    if (!newTeamId.trim()) return;

    setTournament({
      ...tournament,
      teams: [...tournament.teams, Number(newTeamId)],
    });

    setNewTeamId('');
    setIsAddTeamModal(false);
  };

  const isLocked = tournament.status === 'finished';

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex justify-between mb-8 items-center">
          <h1 className="text-3xl font-bold text-gray-800">Gestão do Torneio</h1>

          <div className="flex gap-3">

            {/* Finalizar */}
            {!isLocked && (
              <button
                onClick={finishTournament}
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-md"
              >
                Finalizar
              </button>
            )}

            {/* Eliminar */}
            <button
              onClick={deleteTournament}
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-md"
            >
              Eliminar
            </button>
          </div>
        </div>

        {/* GRID */}
        <div className="grid grid-cols-3 gap-8">

          {/* COL 1 - Detalhes */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Detalhes</h2>

            <div className="space-y-4">

              <div>
                <label className="font-medium text-teal-600">Nome</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.name}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Modalidade</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.modality_id}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Época</label>
                <div className="bg-gray-100 p-3 rounded-md">{tournament.year}</div>
              </div>

              <div>
                <label className="font-medium text-teal-600">Regras</label>
                <pre className="bg-gray-100 p-3 rounded-md whitespace-pre-wrap">
                  {tournament.rules ?? "Nenhuma"}
                </pre>
              </div>

              <div>
                <label className="font-medium text-teal-600">Data de início</label>
                <div className="bg-gray-100 p-3 rounded-md">
                  {tournament.start_date ?? "Não definida"}
                </div>
              </div>

              {!isLocked && (
                <div className="pt-4">
                  <button
                    onClick={openEdit}
                    className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md"
                  >
                    Editar
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* COL 2 - Equipas */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Equipas</h2>

            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {tournament.teams.map(teamId => (
                <div
                  key={teamId}
                  className="bg-gray-100 px-4 py-2 rounded-md text-gray-700"
                >
                  Equipa {teamId}
                </div>
              ))}
            </div>

            {!isLocked && (
              <div className="pt-4">
                <button
                  onClick={() => setIsAddTeamModal(true)}
                  className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md"
                >
                  + Adicionar Equipa
                </button>
              </div>
            )}
          </div>

          {/* COL 3 - Jogos */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Jogos</h2>

            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map(j => (
                <div key={j} className="bg-gray-100 px-4 py-2 rounded-md">
                  Jogo {j}
                </div>
              ))}
            </div>

            {!isLocked && (
              <div className="pt-4">
                <button className="w-full bg-teal-500 hover:bg-teal-600 text-white py-2 rounded-md">
                  + Novo Jogo
                </button>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* ==================== MODAL EDITAR ==================== */}
      {isEditModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">

            <h2 className="text-2xl font-bold mb-6">Editar Torneio</h2>

            <div className="space-y-4">
              <div>
                <label className="font-medium">Nome</label>
                <input
                  className="border w-full px-4 py-2 rounded-md"
                  value={editName}
                  onChange={e => setEditName(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Regras (JSON)</label>
                <textarea
                  className="border w-full px-4 py-2 rounded-md min-h-[80px]"
                  value={editRules}
                  onChange={e => setEditRules(e.target.value)}
                />
              </div>

              <div>
                <label className="font-medium">Data de início</label>
                <input
                  type="date"
                  className="border w-full px-4 py-2 rounded-md"
                  value={editStartDate}
                  onChange={e => setEditStartDate(e.target.value)}
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsEditModal(false)}
                className="flex-1 bg-gray-300 py-2 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={saveEdit}
                className="flex-1 bg-teal-500 text-white py-2 rounded-md"
              >
                Guardar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ==================== MODAL ADD TEAM ==================== */}
      {!isLocked && isAddTeamModal && (
        <div className="fixed inset-0 bg-black/50 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg max-w-md w-full">

            <h2 className="text-2xl font-bold mb-6">Adicionar Equipa</h2>

            <div>
              <label className="font-medium">ID da Equipa</label>
              <input
                type="number"
                className="border w-full px-4 py-2 rounded-md"
                value={newTeamId}
                onChange={e => setNewTeamId(e.target.value)}
              />
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setIsAddTeamModal(false)}
                className="flex-1 bg-gray-300 py-2 rounded-md"
              >
                Cancelar
              </button>
              <button
                onClick={addTeam}
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

export default TorneioDetails;
