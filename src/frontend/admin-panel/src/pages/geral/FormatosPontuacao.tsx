import { useEffect, useState } from "react";
import Sidebar from "../../components/geral_navbar";
import { scoringFormatsApi } from "../../api/scoring-formats";

// Types for the scoring format structure
interface EscalaoRow {
  escalao: string;
  minParticipants: number | null;
  maxParticipants: number | null;
  points: number[];
}

interface ScoringFormat {
  id: string;
  name: string;
  description?: string;
  escaloes: EscalaoRow[];
  created_at?: string;
  updated_at?: string;
}

const FormatosPontuacao = () => {
  const [scoringFormats, setScoringFormats] = useState<ScoringFormat[]>([]);
  const [loading] = useState(false);
  const [error, setError] = useState('');

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ScoringFormat | null>(null);

  // Form states
  const [formatName, setFormatName] = useState('');
  const [formatDescription, setFormatDescription] = useState('');
  const [escaloes, setEscaloes] = useState<EscalaoRow[]>([
    { escalao: 'A', minParticipants: null, maxParticipants: null, points: [] }
  ]);

  const fetchScoringFormats = async () => {
	try {
	//   setError('');
	  const formats = await scoringFormatsApi.getAll();
	  setScoringFormats(formats);
	} catch (err) {
	  console.error('Failed to fetch scoring formats:', err);
	  setError('Erro ao carregar formatos de pontuação');
	}
  };

  useEffect(() => {
	fetchScoringFormats();
  }, []);

  const handleAddEscalao = () => {
    const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    const nextLetter = letters[escaloes.length] || '';
    setEscaloes([
      ...escaloes,
      { escalao: nextLetter, minParticipants: null, maxParticipants: null, points: [] }
    ]);
  };

  const handleRemoveEscalao = (index: number) => {
    setEscaloes(escaloes.filter((_, i) => i !== index));
  };

  const handleEscalaoChange = (index: number, field: keyof EscalaoRow, value: string | number | null) => {
    const newEscaloes = [...escaloes];
    if (field === 'points') {
      // Parse points as comma or space separated numbers
      const pointsArray = String(value).split(/[\s,]+/).map(p => parseInt(p.trim())).filter(p => !isNaN(p));
      newEscaloes[index] = { ...newEscaloes[index], points: pointsArray };
    } else {
      newEscaloes[index] = { ...newEscaloes[index], [field]: value };
    }
    setEscaloes(newEscaloes);
  };

  const handleCreateFormat = async () => {
    if (!formatName.trim()) {
      setError('Por favor, preencha o nome do formato.');
      return;
    }

    if (escaloes.length === 0) {
      setError('Por favor, adicione pelo menos um escalão.');
      return;
    }

    // Validate escaloes
    for (const esc of escaloes) {
      if (!esc.escalao.trim()) {
        setError('Todos os escalões devem ter um nome.');
        return;
      }
      if (esc.points.length === 0) {
        setError('Todos os escalões devem ter pontuações definidas.');
        return;
      }
    }

    try {
      setError('');

    //   TODO: API call to create scoring format
      const newFormat = await scoringFormatsApi.create({
        name: formatName,
        description: formatDescription || undefined,
        escaloes: escaloes,
      });

    //   const newFormat: ScoringFormat = {
    //     id: Date.now().toString(),
    //     name: formatName,
    //     description: formatDescription || undefined,
    //     escaloes: escaloes,
    //     created_at: new Date().toISOString(),
    //   };

      setScoringFormats([...scoringFormats, newFormat]);

      // Reset form
      setFormatName('');
      setFormatDescription('');
      setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: [] }]);
      setIsCreateModalOpen(false);
    } catch (err) {
      console.error('Failed to create scoring format:', err);
      setError('Erro ao criar formato de pontuação');
    }
  };

  const handleViewFormat = (format: ScoringFormat) => {
    setSelectedFormat(format);
    setIsViewModalOpen(true);
  };

  const handleEditFormat = (format: ScoringFormat) => {
    setSelectedFormat(format);
    setFormatName(format.name);
    setFormatDescription(format.description || '');
    setEscaloes(format.escaloes);
    setIsViewModalOpen(false);
    setIsEditModalOpen(true);
  };

  const handleUpdateFormat = async () => {
    if (!formatName.trim()) {
      setError('Por favor, preencha o nome do formato.');
      return;
    }

    if (escaloes.length === 0) {
      setError('Por favor, adicione pelo menos um escalão.');
      return;
    }

    // Validate escaloes
    for (const esc of escaloes) {
      if (!esc.escalao.trim()) {
        setError('Todos os escalões devem ter um nome.');
        return;
      }
      if (esc.points.length === 0) {
        setError('Todos os escalões devem ter pontuações definidas.');
        return;
      }
    }

    try {
      setError('');

      // TODO: API call to update scoring format
      const updatedFormat = await scoringFormatsApi.update(selectedFormat!.id, {
        name: formatName,
        description: formatDescription || undefined,
        escaloes: escaloes,
      });

    //   const updatedFormat: ScoringFormat = {
    //     ...selectedFormat!,
    //     name: formatName,
    //     description: formatDescription || undefined,
    //     escaloes: escaloes,
    //     updated_at: new Date().toISOString(),
    //   };

      setScoringFormats(scoringFormats.map(f =>
        f.id === selectedFormat!.id ? updatedFormat : f
      ));

      // Reset form
      setFormatName('');
      setFormatDescription('');
      setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: [] }]);
      setSelectedFormat(null);
      setIsEditModalOpen(false);
      alert('Formato de pontuação atualizado com sucesso!');
    } catch (err) {
      console.error('Failed to update scoring format:', err);
      setError('Erro ao atualizar formato de pontuação');
    }
  };

  const handleDeleteFormat = async () => {
    if (!selectedFormat) return;

    if (!confirm(`Tem certeza que deseja eliminar "${selectedFormat.name}"?`)) {
      return;
    }

    try {
      setError('');

      // TODO: API call to delete scoring format
      await scoringFormatsApi.delete(selectedFormat.id);

      setScoringFormats(scoringFormats.filter(f => f.id !== selectedFormat.id));
      setIsViewModalOpen(false);
      setSelectedFormat(null);
      alert('Formato de pontuação eliminado com sucesso!');
    } catch (err) {
      console.error('Failed to delete scoring format:', err);
      setError('Erro ao eliminar formato de pontuação');
    }
  };

  const getParticipantsText = (min: number | null, max: number | null) => {
    if (max === null && min === null) return '—';
    if (max === null) return `mais de ${min}`;
    if (min === null) return `até ${max}`;
    if (min === max) return `${min}`;
    return `${min} a ${max}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />

      <div className="p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Formatos de Pontuação</h1>

          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-6 py-3 bg-teal-500 text-white rounded-md hover:bg-teal-600 transition-colors"
          >
            + Adicionar Formato
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

        {/* List */}
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : scoringFormats.length > 0 ? (
            scoringFormats.map(format => (
              <div
                key={format.id}
                className="p-4 bg-gray-100 rounded-md hover:bg-gray-200 cursor-pointer flex justify-between items-center transition-colors"
                onClick={() => handleViewFormat(format)}
              >
                <div>
                  <div className="font-medium text-lg">{format.name}</div>
                  {format.description && (
                    <div className="text-sm text-gray-600 mt-1">{format.description}</div>
                  )}
                  <div className="text-sm text-gray-500 mt-1">
                    {format.escaloes.length} {format.escaloes.length !== 1 ? 'escalões' : 'escalão'}
                  </div>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">Nenhum formato de pontuação encontrado.</p>
          )}
        </div>
      </div>

      {/* ========== CREATE MODAL ========== */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4 overflow-y-auto">
          <div className="bg-white p-8 rounded-lg w-full max-w-4xl my-8">
            <h2 className="text-2xl font-bold mb-6">Criar Formato de Pontuação</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-6">
              {/* Name */}
              <div>
                <label className="block font-medium mb-2">
                  Nome do Formato <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Ex: Modalidades Coletivas Recorrentes"
                  value={formatName}
                  onChange={e => setFormatName(e.target.value)}
                />
              </div>

              {/* Description */}
              <div>
                <label className="block font-medium mb-2">Descrição</label>
                <textarea
                  className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Descrição opcional"
                  rows={2}
                  value={formatDescription}
                  onChange={e => setFormatDescription(e.target.value)}
                />
              </div>

              {/* Escalões Section */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="block font-medium">
                    Escalões <span className="text-red-500">*</span>
                  </label>
                  <button
                    onClick={handleAddEscalao}
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm"
                  >
                    + Adicionar Escalão
                  </button>
                </div>

                <div className="space-y-4">
                  {escaloes.map((esc, index) => (
                    <div key={index} className="border border-gray-300 rounded-md p-4 bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-medium text-lg">Escalão {esc.escalao}</h3>
                        {escaloes.length > 1 && (
                          <button
                            onClick={() => handleRemoveEscalao(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        {/* Escalão name */}
                        <div>
                          <label className="block text-sm font-medium mb-1">Nome do Escalão</label>
                          <input
                            type="text"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="A, B, C..."
                            value={esc.escalao}
                            onChange={e => handleEscalaoChange(index, 'escalao', e.target.value)}
                          />
                        </div>

                        {/* Min participants */}
                        <div>
                          <label className="block text-sm font-medium mb-1">Mín. Participantes</label>
                          <input
                            type="number"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 32"
                            value={esc.minParticipants ?? ''}
                            onChange={e => handleEscalaoChange(index, 'minParticipants', e.target.value ? parseInt(e.target.value) : null)}
                          />
                        </div>

                        {/* Max participants */}
                        <div>
                          <label className="block text-sm font-medium mb-1">Máx. Participantes</label>
                          <input
                            type="number"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 40"
                            value={esc.maxParticipants ?? ''}
                            onChange={e => handleEscalaoChange(index, 'maxParticipants', e.target.value ? parseInt(e.target.value) : null)}
                          />
                        </div>
                      </div>

                      {/* Points */}
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Pontuações (1º, 2º, 3º, ...) <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                          placeholder="Ex: 140 130 120 110 90 80 70 60 40 30 20 10"
                          value={esc.points.join(' ')}
                          onChange={e => handleEscalaoChange(index, 'points', e.target.value)}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Separe os valores por espaço ou vírgula. Ordem: 1º lugar, 2º lugar, 3º lugar, etc.
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 mt-6">
              <button
                className="flex-1 bg-gray-300 py-2 rounded-md hover:bg-gray-400 transition-colors"
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setFormatName('');
                  setFormatDescription('');
                  setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: [] }]);
                  setError('');
                }}
              >
                Cancelar
              </button>
              <button
                className="flex-1 bg-teal-500 py-2 text-white rounded-md hover:bg-teal-600 transition-colors"
                onClick={handleCreateFormat}
              >
                Criar Formato
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========== VIEW/DETAILS MODAL ========== */}
      {isViewModalOpen && selectedFormat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4 overflow-y-auto">
          <div className="bg-white p-8 rounded-lg w-full max-w-5xl my-8">
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold">{selectedFormat.name}</h2>
              <button
                onClick={() => setIsViewModalOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {selectedFormat.description && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-500 mb-1">Descrição</label>
                <p className="text-gray-900">{selectedFormat.description}</p>
              </div>
            )}

            {/* Escalões Table */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Tabela de Pontuação</h3>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 px-4 py-2 text-left">Escalão</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">Participantes</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">1º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">2º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">3º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">4º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">5º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">6º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">7º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">8º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">9º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">10º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">11º</th>
                      <th className="border border-gray-300 px-4 py-2 text-left">12º</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedFormat.escaloes.map((esc, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="border border-gray-300 px-4 py-2 font-medium">{esc.escalao}</td>
                        <td className="border border-gray-300 px-4 py-2">
                          {getParticipantsText(esc.minParticipants, esc.maxParticipants)}
                        </td>
                        {[...Array(12)].map((_, i) => (
                          <td key={i} className="border border-gray-300 px-4 py-2 text-center">
                            {esc.points[i] ?? '—'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {selectedFormat.created_at && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-500 mb-1">Data de Criação</label>
                <p className="text-gray-900">
                  {new Date(selectedFormat.created_at).toLocaleDateString('pt-PT', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                  })}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4 pt-4 border-t">
              <button
                onClick={handleDeleteFormat}
                className="px-6 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
              >
                Eliminar
              </button>
              <button
                onClick={() => handleEditFormat(selectedFormat)}
                className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Editar
              </button>
              <button
                onClick={() => setIsViewModalOpen(false)}
                className="flex-1 px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========== EDIT MODAL ========== */}
      {isEditModalOpen && selectedFormat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4 overflow-y-auto">
          <div className="bg-white p-8 rounded-lg w-full max-w-4xl my-8">
            <h2 className="text-2xl font-bold mb-6">Editar Formato de Pontuação</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-6">
              {/* Name */}
              <div>
                <label className="block font-medium mb-2">
                  Nome do Formato <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Ex: Modalidades Coletivas Recorrentes"
                  value={formatName}
                  onChange={e => setFormatName(e.target.value)}
                />
              </div>

              {/* Description */}
              <div>
                <label className="block font-medium mb-2">Descrição</label>
                <textarea
                  className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Descrição opcional"
                  rows={2}
                  value={formatDescription}
                  onChange={e => setFormatDescription(e.target.value)}
                />
              </div>

              {/* Escalões Section */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="block font-medium">
                    Escalões <span className="text-red-500">*</span>
                  </label>
                  <button
                    onClick={handleAddEscalao}
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm"
                  >
                    + Adicionar Escalão
                  </button>
                </div>

                <div className="space-y-4">
                  {escaloes.map((esc, index) => (
                    <div key={index} className="border border-gray-300 rounded-md p-4 bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-medium text-lg">Escalão {esc.escalao}</h3>
                        {escaloes.length > 1 && (
                          <button
                            onClick={() => handleRemoveEscalao(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        {/* Escalão name */}
                        <div>
                          <label className="block text-sm font-medium mb-1">Nome do Escalão</label>
                          <input
                            type="text"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="A, B, C..."
                            value={esc.escalao}
                            onChange={e => handleEscalaoChange(index, 'escalao', e.target.value)}
                          />
                        </div>

                        {/* Min participants */}
                        <div>
                          <label className="block text-sm font-medium mb-1">Mín. Participantes</label>
                          <input
                            type="number"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 32"
                            value={esc.minParticipants ?? ''}
                            onChange={e => handleEscalaoChange(index, 'minParticipants', e.target.value ? parseInt(e.target.value) : null)}
                          />
                        </div>

                        {/* Max participants */}
                        <div>
                          <label className="block text-sm font-medium mb-1">Máx. Participantes</label>
                          <input
                            type="number"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 40"
                            value={esc.maxParticipants ?? ''}
                            onChange={e => handleEscalaoChange(index, 'maxParticipants', e.target.value ? parseInt(e.target.value) : null)}
                          />
                        </div>
                      </div>

                      {/* Points */}
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Pontuações (1º, 2º, 3º, ...) <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                          placeholder="Ex: 140 130 120 110 90 80 70 60 40 30 20 10"
                          value={esc.points.join(' ')}
                          onChange={e => handleEscalaoChange(index, 'points', e.target.value)}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Separe os valores por espaço ou vírgula. Ordem: 1º lugar, 2º lugar, 3º lugar, etc.
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 mt-6">
              <button
                className="flex-1 bg-gray-300 py-2 rounded-md hover:bg-gray-400 transition-colors"
                onClick={() => {
                  setIsEditModalOpen(false);
                  setFormatName('');
                  setFormatDescription('');
                  setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: [] }]);
                  setSelectedFormat(null);
                  setError('');
                }}
              >
                Cancelar
              </button>
              <button
                className="flex-1 bg-teal-500 py-2 text-white rounded-md hover:bg-teal-600 transition-colors"
                onClick={handleUpdateFormat}
              >
                Guardar Alterações
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FormatosPontuacao;
