import { useEffect, useState } from "react";
import HelpTooltip from '../../components/HelpTooltip';
import ConfirmModal from "../../components/ConfirmModal";
import { modalityTypesApi, type ModalityTypeListItem } from "../../api/modality-types";
import { useNotification } from '../../contexts/NotificationProvider';
import { btn } from '../../styles/buttonStyles';
import DefinedStatesMenuComponent from "../../components/utils/costum_menus/DefinedStatesMenuComponent";

// Types for the scoring format structure
interface EscalaoRow {
  escalao: string;
  minParticipants: number | null;
  maxParticipants: number | null;
  points: string;
}

const parsePoints = (raw: string): number[] =>
  raw.split(/[\s,]+/).map(p => parseInt(p.trim())).filter(p => !isNaN(p));


const FormatosPontuacao = () => {
  const [scoringFormats, setModalityTypes] = useState<ModalityTypeListItem[]>([]);
  const [loading] = useState(false);
  const { notify } = useNotification();

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ModalityTypeListItem | null>(null);
  const [deletingFormat, setDeletingFormat] = useState(false);

  // Form states
  const [formatName, setFormatName] = useState('');
  const [formatDescription, setFormatDescription] = useState('');
  const [isPlayoff, setIsPlayoff] = useState(false);
  const [escaloes, setEscaloes] = useState<EscalaoRow[]>([
    { escalao: 'A', minParticipants: null, maxParticipants: null, points: '' }
  ]);
    const [tournamentCompetitorType, setTournamentCompetitorType] = useState<'individual' | 'team'>('individual');

useEffect(() => {
	let mounted = true;

	(async () => {
		try {
			const formats = await modalityTypesApi.getAll();
			if (!mounted) return;
			setModalityTypes(formats);
		} catch (err) {
			console.error('Failed to fetch scoring formats:', err);
			if (!mounted) return;
			notify('Não foi possível carregar os formatos de prova. Tente recarregar a página.', 'error');
		}
	})();

	return () => {
		mounted = false;
	};
}, []);

  const handleAddEscalao = () => {
    const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    const nextLetter = letters[escaloes.length] || '';
    setEscaloes([
      ...escaloes,
      { escalao: nextLetter, minParticipants: null, maxParticipants: null, points: '' }
    ]);
  };

  const handleRemoveEscalao = (index: number) => {
    setEscaloes(escaloes.filter((_, i) => i !== index));
  };

  const handleEscalaoChange = (index: number, field: keyof EscalaoRow, value: string | number | null) => {
    const newEscaloes = [...escaloes];
    newEscaloes[index] = { ...newEscaloes[index], [field]: value };
    setEscaloes(newEscaloes);
  };

  const handleCreateFormat = async () => {
    if (!formatName.trim()) {
      notify('Por favor, preencha o nome do formato.', 'error');
      return;
    }

    if (escaloes.length === 0) {
      notify('Por favor, adicione pelo menos um escalão.', 'error');
      return;
    }

    // Validate escaloes
    for (const esc of escaloes) {
      if (!esc.escalao.trim()) {
        notify('Todos os escalões devem ter um nome.', 'error');
        return;
      }
      if (parsePoints(esc.points).length === 0) {
        notify('Todos os escalões devem ter pontuações definidas.', 'error');
        return;
      }
    }

    try {

      const newFormat = await modalityTypesApi.create({
        name: formatName,
        description: formatDescription || undefined,
        is_playoff: isPlayoff,
        escaloes: escaloes.map(esc => ({ ...esc, points: parsePoints(esc.points) })),
         tournament_competitor_type: tournamentCompetitorType,
      });

      setModalityTypes([...scoringFormats, newFormat]);

      // Reset form
      setFormatName('');
      setFormatDescription('');
      setIsPlayoff(false);
        setTournamentCompetitorType('individual');
      setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: '' }]);
      setIsCreateModalOpen(false);
    } catch (err: unknown) {
      console.error('Failed to create scoring format:', err);
      const msg = err instanceof Error ? err.message : '';
      if (msg.toLowerCase().includes('playoff')) {
        notify('Já existe um formato de playoff. Só pode existir um formato de playoff de cada vez.', 'error');
      } else {
        notify('Não foi possível criar o formato de prova. Verifique os dados e tente novamente.', 'error');
      }
    }
  };

  const handleViewFormat = (format: ModalityTypeListItem) => {
    setSelectedFormat(format);
    setIsViewModalOpen(true);
  };

  const handleEditFormat = (format: ModalityTypeListItem) => {
    setSelectedFormat(format);
    setFormatName(format.name);
    setFormatDescription(format.description || '');
    setIsPlayoff(format.is_playoff);
    setTournamentCompetitorType(format.tournament_competitor_type);
    setEscaloes(format.escaloes.map(esc => ({ ...esc, points: esc.points.join(' ') })));
    setIsViewModalOpen(false);
    setIsEditModalOpen(true);
  };

  const handleUpdateFormat = async () => {
    if (!formatName.trim()) {
      notify('Por favor, preencha o nome do formato.', 'error');
      return;
    }

    if (escaloes.length === 0) {
      notify('Por favor, adicione pelo menos um escalão.', 'error');
      return;
    }

    // Validate escaloes
    for (const esc of escaloes) {
      if (!esc.escalao.trim()) {
        notify('Todos os escalões devem ter um nome.', 'error');
        return;
      }
      if (parsePoints(esc.points).length === 0) {
        notify('Todos os escalões devem ter pontuações definidas.', 'error');
        return;
      }
    }

    // If user is deselecting playoff, require tournament_competitor_type
    if (selectedFormat?.is_playoff && !isPlayoff && !tournamentCompetitorType) {
      notify('Selecione o tipo de competidor (Individual ou Equipa) ao remover o formato playoff.', 'error');
      return;
    }

    try {

      // TODO: API call to update scoring format
      const updatedFormat = await modalityTypesApi.update(selectedFormat!.id, {
        name: formatName,
        description: formatDescription || undefined,
        is_playoff: isPlayoff,
        escaloes: escaloes.map(esc => ({ ...esc, points: parsePoints(esc.points) })),
         tournament_competitor_type: tournamentCompetitorType,
      });

      setModalityTypes(scoringFormats.map(f =>
        f.id === selectedFormat!.id ? updatedFormat : f
      ));

      // Reset form
      setFormatName('');
      setFormatDescription('');
      setIsPlayoff(false);
        setTournamentCompetitorType('individual');
      setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: '' }]);
      setSelectedFormat(null);
      setIsEditModalOpen(false);
      notify('Formato de prova atualizado com sucesso!', 'success');
    } catch (err: unknown) {
      console.error('Failed to update scoring format:', err);
      const msg = err instanceof Error ? err.message : '';
      if (msg.toLowerCase().includes('playoff')) {
        notify('Já existe um formato de playoff. Só pode existir um formato de playoff de cada vez.', 'error');
      } else {
        notify('Não foi possível guardar as alterações ao formato de prova. Tente novamente.', 'error');
      }
    }
  };

  const handleDeleteFormat = async () => {
    if (!selectedFormat) return;

    setIsDeleteModalOpen(true);
  };

  const confirmDeleteFormat = async () => {
    if (!selectedFormat) return;

    try {
      setDeletingFormat(true);

      // TODO: API call to delete scoring format
      await modalityTypesApi.delete(selectedFormat.id);

      setModalityTypes(scoringFormats.filter(f => f.id !== selectedFormat.id));
      setIsDeleteModalOpen(false);
      setIsViewModalOpen(false);
      setSelectedFormat(null);
      notify('Formato de prova eliminado com sucesso!', 'success');
    } catch (err) {
      console.error('Failed to delete scoring format:', err);
      notify('Não foi possível eliminar o formato de prova. Poderá estar em uso por alguma modalidade.', 'error');
    } finally {
      setDeletingFormat(false);
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
      <div className="flex-1 p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Formatos de Prova</h1>

          <button
            onClick={() => setIsCreateModalOpen(true)}
            className={`px-6 py-3 ${btn.primary} rounded-md transition-colors`}
          >
            + Adicionar Formato
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-teal-500 border-r-transparent"></div>
              <p className="mt-2 text-gray-600">A carregar...</p>
            </div>
          ) : scoringFormats.length > 0 ? (
            [...scoringFormats].sort((a, b) => a.name.localeCompare(b.name)).map(format => (
              <button
                key={format.id}
                type="button"
                className="w-full text-left p-4 bg-gray-100 rounded-md hover:bg-gray-200 flex justify-between items-center transition-colors focus:outline-none focus:ring-2 focus:ring-teal-500"
                onClick={() => handleViewFormat(format)}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-lg">{format.name}</span>
                    {format.is_playoff && (
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-semibold rounded-full border border-amber-300">
                        Playoff
                      </span>
                    )}
                    {!format.is_playoff && format.tournament_competitor_type && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${format.tournament_competitor_type === 'individual' ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-green-100 text-green-700 border-green-300'}`}>
                        {format.tournament_competitor_type === 'individual' ? 'Individual' : 'Equipa'}
                      </span>
                    )}
                  </div>
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
              </button>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">Nenhum formato de prova encontrado.</p>
          )}
        </div>
        {isCreateModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4 overflow-y-auto">
            <div className="bg-white p-8 rounded-lg w-full max-w-4xl my-8">
              <h2 className="text-2xl font-bold mb-6">Criar Formato de Prova</h2>

              <div className="space-y-6">
                <div>
                  <label className="block font-medium mb-2">
                    Nome do Formato <HelpTooltip text="Nome único que identifica este conjunto de regras de pontuação. Ex: 'Modalidades Coletivas Recorrentes'." className="ml-1" /> <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Ex: Modalidades Coletivas Recorrentes"
                    value={formatName}
                    onChange={e => setFormatName(e.target.value)}
                  />
                </div>

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

                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="create-is-playoff"
                    checked={isPlayoff}
                    onChange={e => setIsPlayoff(e.target.checked)}
                    className="w-4 h-4 accent-amber-500 cursor-pointer"
                  />
                  <label htmlFor="create-is-playoff" className="font-medium cursor-pointer select-none">
                    Formato Playoff
                  </label>
                  <span className="text-sm text-gray-500">(só pode existir um formato de playoff de cada vez)</span>
                </div>

                {!isPlayoff && (
                  <div>
                    <label className="block font-medium mb-2">
                      Tipo de Competidor <span className="text-red-500">*</span>
                    </label>
                    <DefinedStatesMenuComponent
                      states={[
                        {value: 'individual', label: 'Individual'},
                        {value: 'team', label: 'Equipa'},
                      ]}
                      onSelect={(value) => setTournamentCompetitorType(value as 'individual' | 'team')}
                    />
                  </div>
                )}

                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="block font-medium">
                      Escalões <HelpTooltip text="Categorias de participação dentro do formato (ex: A, B, C). Cada escalão tem os seus próprios limites de participantes e tabela de pontuações." className="ml-1" /> <span className="text-red-500">*</span>
                    </label>
                    <button
                      onClick={handleAddEscalao}
                      className={`px-4 py-2 ${btn.info} rounded-md transition-colors text-sm`}
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
                              className="text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                          <div>
                            <label className="block text-sm font-medium mb-1">Nome do Escalão <HelpTooltip text="Identificador do escalão, tipicamente uma letra (A, B, C) ou nome descritivo." className="ml-1" /></label>
                            <input
                              type="text"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="A, B, C..."
                              value={esc.escalao}
                              onChange={e => handleEscalaoChange(index, 'escalao', e.target.value)}
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1">Mín. Participantes <HelpTooltip text="Número mínimo de equipas/participantes necessários para este escalão se realizar. Deixe vazio se não aplicar." className="ml-1" /></label>
                            <input
                              type="number"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="Ex: 32"
                              value={esc.minParticipants ?? ''}
                              onChange={e => handleEscalaoChange(index, 'minParticipants', e.target.value ? parseInt(e.target.value) : null)}
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1">Máx. Participantes <HelpTooltip text="Número máximo de equipas/participantes permitidos neste escalão. Deixe vazio se não aplicar." className="ml-1" /></label>
                            <input
                              type="number"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="Ex: 40"
                              value={esc.maxParticipants ?? ''}
                              onChange={e => handleEscalaoChange(index, 'maxParticipants', e.target.value ? parseInt(e.target.value) : null)}
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-1">
                            Pontuações (1º, 2º, 3º, ...) <HelpTooltip text="Pontos atribuídos por posição final. O 1º valor é para o 1º lugar, o 2º para o 2º lugar, etc. Separe por espaços ou vírgulas." className="ml-1" position="top" /> <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="text"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 140 130 120 110 90 80 70 60 40 30 20 10"
                            value={esc.points}
                            onChange={e => handleEscalaoChange(index, 'points', e.target.value)}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  className={`flex-1 ${btn.secondary} py-2 rounded-md`}
                  onClick={() => {
                    setIsCreateModalOpen(false);
                    setFormatName('');
                    setFormatDescription('');
                    setIsPlayoff(false);
                    setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: '' }]);
                  }}
                >
                  Cancelar
                </button>
                <button
                  className={`flex-1 ${btn.primary} py-2 rounded-md transition-colors`}
                  onClick={handleCreateFormat}
                >
                  Criar Formato
                </button>
              </div>
            </div>
          </div>
        )}

        {isViewModalOpen && selectedFormat && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-4 overflow-y-auto">
            <div className="bg-white p-8 rounded-lg w-full max-w-5xl my-8">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold">{selectedFormat.name}</h2>
                <button
                  onClick={() => setIsViewModalOpen(false)}
                  className="text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-400 rounded"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="mb-4 flex items-center gap-2">
                {selectedFormat.is_playoff ? (
                  <span className="px-3 py-1 bg-amber-100 text-amber-700 text-sm font-semibold rounded-full border border-amber-300">
                    Formato Playoff
                  </span>
                ) : (
                  <>
                  <span className="px-3 py-1 bg-gray-100 text-gray-500 text-sm rounded-full border border-gray-200">
                    Formato Regular
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${selectedFormat.tournament_competitor_type === 'individual' ? 'bg-blue-100 text-blue-700 border-blue-300' : 'bg-green-100 text-green-700 border-green-300'}`}>
                    {selectedFormat.tournament_competitor_type === 'individual' ? 'Individual' : 'Equipa'}
                  </span>
                  </>
                )}
              </div>

              {selectedFormat.description && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-500 mb-1">Descrição</label>
                  <p className="text-gray-900">{selectedFormat.description}</p>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Tabela de Prova</h3>
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

              <div className="flex gap-4 pt-4 border-t">
                <button
                  onClick={handleDeleteFormat}
                  className={`px-6 py-2 ${btn.dangerLight} rounded transition-colors`}
                >
                  Eliminar
                </button>
                <button
                  onClick={() => handleEditFormat(selectedFormat)}
                  className={`px-6 py-2 ${btn.info} rounded transition-colors`}
                >
                  Editar
                </button>
                <button
                  onClick={() => setIsViewModalOpen(false)}
                  className={`flex-1 px-6 py-2 ${btn.secondaryAlt} rounded transition-colors`}
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        )}

        {isEditModalOpen && selectedFormat && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-start z-50 p-4 overflow-y-auto">
            <div className="bg-white p-8 rounded-lg w-full max-w-4xl my-8">
              <h2 className="text-2xl font-bold mb-6">Editar Formato de Prova</h2>

              <div className="space-y-6">
                <div>
                  <label className="block font-medium mb-2">
                    Nome do Formato <HelpTooltip text="Nome único que identifica este conjunto de regras de pontuação. Ex: 'Modalidades Coletivas Recorrentes'." className="ml-1" /> <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    className="border px-4 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                    placeholder="Ex: Modalidades Coletivas Recorrentes"
                    value={formatName}
                    onChange={e => setFormatName(e.target.value)}
                  />
                </div>

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

                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="edit-is-playoff"
                    checked={isPlayoff}
                    onChange={e => setIsPlayoff(e.target.checked)}
                    className="w-4 h-4 accent-amber-500 cursor-pointer"
                  />
                  <label htmlFor="edit-is-playoff" className="font-medium cursor-pointer select-none">
                    Formato Playoff
                  </label>
                  <span className="text-sm text-gray-500">(só pode existir um formato de playoff de cada vez)</span>
                </div>

                {!isPlayoff && (
                  <div>
                    <label className="block font-medium mb-2">
                      Tipo de Competidor <span className="text-red-500">*</span>
                    </label>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        className={`flex-1 py-2 rounded-md border transition-colors font-semibold ${tournamentCompetitorType === 'team' ? 'bg-teal-500 text-white border-teal-600' : 'bg-white text-teal-700 border-gray-300'}`}
                        onClick={() => setTournamentCompetitorType('team')}
                      >
                        Equipa
                      </button>
                      <button
                        type="button"
                        className={`flex-1 py-2 rounded-md border transition-colors font-semibold ${tournamentCompetitorType === 'individual' ? 'bg-teal-500 text-white border-teal-600' : 'bg-white text-teal-700 border-gray-300'}`}
                        onClick={() => setTournamentCompetitorType('individual')}
                      >
                        Individual
                      </button>
                    </div>
                  </div>
                )}

                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="block font-medium">
                      Escalões <HelpTooltip text="Categorias de participação dentro do formato (ex: A, B, C). Cada escalão tem os seus próprios limites de participantes e tabela de pontuações." className="ml-1" /> <span className="text-red-500">*</span>
                    </label>
                  </div>

                  <div className="space-y-4">
                    {escaloes.map((esc, index) => (
                      <div key={index} className="border border-gray-300 rounded-md p-4 bg-gray-50">
                        <div className="flex justify-between items-start mb-3">
                          <h3 className="font-medium text-lg">Escalão {esc.escalao}</h3>
                          {escaloes.length > 1 && (
                            <button
                              onClick={() => handleRemoveEscalao(index)}
                              className="text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                          <div>
                            <label className="block text-sm font-medium mb-1">Nome do Escalão <HelpTooltip text="Identificador do escalão, tipicamente uma letra (A, B, C) ou nome descritivo." className="ml-1" /></label>
                            <input
                              type="text"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="A, B, C..."
                              value={esc.escalao}
                              onChange={e => handleEscalaoChange(index, 'escalao', e.target.value)}
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1">Mín. Participantes <HelpTooltip text="Número mínimo de equipas/participantes necessários para este escalão se realizar. Deixe vazio se não aplicar." className="ml-1" /></label>
                            <input
                              type="number"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="Ex: 32"
                              value={esc.minParticipants ?? ''}
                              onChange={e => handleEscalaoChange(index, 'minParticipants', e.target.value ? parseInt(e.target.value) : null)}
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1">Máx. Participantes <HelpTooltip text="Número máximo de equipas/participantes permitidos neste escalão. Deixe vazio se não aplicar." className="ml-1" /></label>
                            <input
                              type="number"
                              className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                              placeholder="Ex: 40"
                              value={esc.maxParticipants ?? ''}
                              onChange={e => handleEscalaoChange(index, 'maxParticipants', e.target.value ? parseInt(e.target.value) : null)}
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-1">
                            Pontuações (1º, 2º, 3º, ...) <HelpTooltip text="Pontos atribuídos por posição final. O 1º valor é para o 1º lugar, o 2º para o 2º lugar, etc. Separe por espaços ou vírgulas." className="ml-1" position="top" /> <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="text"
                            className="border px-3 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-teal-500"
                            placeholder="Ex: 140 130 120 110 90 80 70 60 40 30 20 10"
                            value={esc.points}
                            onChange={e => handleEscalaoChange(index, 'points', e.target.value)}
                          />
                        </div>
                      </div>
                    ))}
            <button
            onClick={handleAddEscalao}
            className={`px-4 py-2 ${btn.info} rounded-md transition-colors text-sm`}
            >
            + Adicionar Escalão
            </button>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  className={`flex-1 ${btn.secondary} py-2 rounded-md`}
                  onClick={() => {
                    setIsEditModalOpen(false);
                    setFormatName('');
                    setFormatDescription('');
                    setIsPlayoff(false);
                    setEscaloes([{ escalao: 'A', minParticipants: null, maxParticipants: null, points: '' }]);
                    setSelectedFormat(null);
                  }}
                >
                  Cancelar
                </button>
                <button
                  className={`flex-1 ${btn.primary} py-2 rounded-md transition-colors`}
                  onClick={handleUpdateFormat}
                >
                  Guardar Alterações
                </button>
              </div>
            </div>
          </div>
        )}

        <ConfirmModal
          isOpen={isDeleteModalOpen}
          title="Eliminar formato de prova"
          message={selectedFormat ? `Tem certeza que deseja eliminar "${selectedFormat.name}"?` : ''}
          confirmLabel="Eliminar"
          variant="danger"
          loading={deletingFormat}
          onCancel={() => {
            if (!deletingFormat) {
              setIsDeleteModalOpen(false);
            }
          }}
          onConfirm={confirmDeleteFormat}
        />
      </div>
  );
};

export default FormatosPontuacao;
